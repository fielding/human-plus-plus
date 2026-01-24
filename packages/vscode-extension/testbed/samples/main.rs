//! Human++ Rust Sample
//!
//! Lock-free concurrent queue with backoff strategy.

use std::sync::atomic::{AtomicPtr, AtomicUsize, Ordering};
use std::ptr;
use std::thread;
use std::time::Duration;

/// Node in the lock-free queue
struct Node<T> {
    value: Option<T>,
    next: AtomicPtr<Node<T>>,
}

impl<T> Node<T> {
    fn new(value: Option<T>) -> *mut Self {
        Box::into_raw(Box::new(Node {
            value,
            next: AtomicPtr::new(ptr::null_mut()),
        }))
    }

    fn sentinel() -> *mut Self {
        Self::new(None)
    }
}

/// Exponential backoff for contention
struct Backoff {
    current: u32,
    max: u32,
}

impl Backoff {
    fn new() -> Self {
        Backoff {
            current: 1,
            max: 1024,
        }
    }

    fn spin(&mut self) {
        for _ in 0..self.current {
            std::hint::spin_loop();
        }
        self.current = (self.current * 2).min(self.max);
    }

    fn reset(&mut self) {
        self.current = 1;
    }
}

// !! This queue uses unsafe code - review carefully before modifying
pub struct LockFreeQueue<T> {
    head: AtomicPtr<Node<T>>,
    tail: AtomicPtr<Node<T>>,
    len: AtomicUsize,
}

impl<T> LockFreeQueue<T> {
    pub fn new() -> Self {
        let sentinel = Node::sentinel();
        LockFreeQueue {
            head: AtomicPtr::new(sentinel),
            tail: AtomicPtr::new(sentinel),
            len: AtomicUsize::new(0),
        }
    }

    pub fn len(&self) -> usize {
        self.len.load(Ordering::Relaxed)
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    pub fn push(&self, value: T) {
        let new_node = Node::new(Some(value));
        let mut backoff = Backoff::new();

        loop {
            let tail = self.tail.load(Ordering::Acquire);
            let tail_ref = unsafe { &*tail };
            let next = tail_ref.next.load(Ordering::Acquire);

            if next.is_null() {
                if tail_ref
                    .next
                    .compare_exchange(
                        ptr::null_mut(),
                        new_node,
                        Ordering::Release,
                        Ordering::Relaxed,
                    )
                    .is_ok()
                {
                    let _ = self.tail.compare_exchange(
                        tail,
                        new_node,
                        Ordering::Release,
                        Ordering::Relaxed,
                    );
                    self.len.fetch_add(1, Ordering::Relaxed);
                    return;
                }
            } else {
                let _ = self.tail.compare_exchange(
                    tail,
                    next,
                    Ordering::Release,
                    Ordering::Relaxed,
                );
            }
            backoff.spin();
        }
    }

    // ?? Should we add a try_pop with timeout?
    pub fn pop(&self) -> Option<T> {
        let mut backoff = Backoff::new();

        loop {
            let head = self.head.load(Ordering::Acquire);
            let tail = self.tail.load(Ordering::Acquire);
            let head_ref = unsafe { &*head };
            let next = head_ref.next.load(Ordering::Acquire);

            if head == tail {
                if next.is_null() {
                    return None;
                }
                let _ = self.tail.compare_exchange(
                    tail,
                    next,
                    Ordering::Release,
                    Ordering::Relaxed,
                );
            } else if !next.is_null() {
                let next_ref = unsafe { &*next };
                if self
                    .head
                    .compare_exchange(head, next, Ordering::Release, Ordering::Relaxed)
                    .is_ok()
                {
                    let value = unsafe { ptr::read(&next_ref.value) };
                    unsafe { drop(Box::from_raw(head)) };
                    self.len.fetch_sub(1, Ordering::Relaxed);
                    return value;
                }
            }
            backoff.spin();
        }
    }
}

impl<T> Drop for LockFreeQueue<T> {
    fn drop(&mut self) {
        while self.pop().is_some() {}
        let head = self.head.load(Ordering::Relaxed);
        unsafe { drop(Box::from_raw(head)) };
    }
}

unsafe impl<T: Send> Send for LockFreeQueue<T> {}
unsafe impl<T: Send> Sync for LockFreeQueue<T> {}

// >> All public queue operations must maintain these invariants
impl<T> Default for LockFreeQueue<T> {
    fn default() -> Self {
        Self::new()
    }
}

fn main() {
    use std::sync::Arc;

    let queue = Arc::new(LockFreeQueue::new());
    let mut handles = vec![];

    // Spawn producer threads
    for i in 0..4 {
        let q = Arc::clone(&queue);
        handles.push(thread::spawn(move || {
            for j in 0..1000 {
                q.push(i * 1000 + j);
            }
        }));
    }

    // Spawn consumer threads
    for _ in 0..2 {
        let q = Arc::clone(&queue);
        handles.push(thread::spawn(move || {
            let mut count = 0;
            loop {
                if q.pop().is_some() {
                    count += 1;
                } else {
                    thread::sleep(Duration::from_micros(100));
                }
                if count >= 2000 {
                    break;
                }
            }
            count
        }));
    }

    for handle in handles {
        let _ = handle.join();
    }

    println!("Final queue length: {}", queue.len());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_push_pop() {
        let queue = LockFreeQueue::new();
        queue.push(1);
        queue.push(2);
        queue.push(3);

        assert_eq!(queue.pop(), Some(1));
        assert_eq!(queue.pop(), Some(2));
        assert_eq!(queue.pop(), Some(3));
        assert_eq!(queue.pop(), None);
    }

    #[test]
    fn test_empty_queue() {
        let queue: LockFreeQueue<i32> = LockFreeQueue::new();
        assert!(queue.is_empty());
        assert_eq!(queue.pop(), None);
    }
}
