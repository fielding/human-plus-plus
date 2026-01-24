/**
 * Human++ C Sample
 *
 * Memory pool allocator with alignment support.
 */

#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define POOL_DEFAULT_BLOCK_SIZE (64 * 1024)  /* 64 KB */
#define POOL_ALIGNMENT 16

typedef struct Block {
    struct Block *next;
    size_t size;
    size_t used;
    uint8_t data[];
} Block;

typedef struct MemoryPool {
    Block *head;
    Block *current;
    size_t block_size;
    size_t total_allocated;
    size_t total_used;
} MemoryPool;

static inline size_t align_up(size_t n, size_t alignment) {
    return (n + alignment - 1) & ~(alignment - 1);
}

static Block *block_create(size_t min_size) {
    size_t size = min_size > POOL_DEFAULT_BLOCK_SIZE ? min_size : POOL_DEFAULT_BLOCK_SIZE;
    Block *block = (Block *)malloc(sizeof(Block) + size);
    if (!block) return NULL;

    block->next = NULL;
    block->size = size;
    block->used = 0;
    return block;
}

// !! Pool does not track individual allocations - cannot free single objects
MemoryPool *pool_create(size_t block_size) {
    MemoryPool *pool = (MemoryPool *)malloc(sizeof(MemoryPool));
    if (!pool) return NULL;

    pool->block_size = block_size > 0 ? block_size : POOL_DEFAULT_BLOCK_SIZE;
    pool->head = block_create(pool->block_size);
    pool->current = pool->head;
    pool->total_allocated = pool->head ? pool->head->size : 0;
    pool->total_used = 0;

    if (!pool->head) {
        free(pool);
        return NULL;
    }

    return pool;
}

void pool_destroy(MemoryPool *pool) {
    if (!pool) return;

    Block *block = pool->head;
    while (block) {
        Block *next = block->next;
        free(block);
        block = next;
    }
    free(pool);
}

void *pool_alloc(MemoryPool *pool, size_t size) {
    if (!pool || size == 0) return NULL;

    size_t aligned_size = align_up(size, POOL_ALIGNMENT);
    Block *block = pool->current;

    /* Try to allocate from current block */
    if (block->used + aligned_size <= block->size) {
        void *ptr = block->data + block->used;
        block->used += aligned_size;
        pool->total_used += aligned_size;
        return ptr;
    }

    /* Need a new block */
    size_t new_block_size = aligned_size > pool->block_size ? aligned_size : pool->block_size;
    Block *new_block = block_create(new_block_size);
    if (!new_block) return NULL;

    block->next = new_block;
    pool->current = new_block;
    pool->total_allocated += new_block->size;

    void *ptr = new_block->data;
    new_block->used = aligned_size;
    pool->total_used += aligned_size;
    return ptr;
}

// ?? Should we add pool_realloc for resizing allocations?
void *pool_calloc(MemoryPool *pool, size_t count, size_t size) {
    size_t total = count * size;
    if (count != 0 && total / count != size) {
        return NULL;  /* Overflow */
    }

    void *ptr = pool_alloc(pool, total);
    if (ptr) {
        memset(ptr, 0, total);
    }
    return ptr;
}

char *pool_strdup(MemoryPool *pool, const char *str) {
    if (!str) return NULL;

    size_t len = strlen(str) + 1;
    char *copy = (char *)pool_alloc(pool, len);
    if (copy) {
        memcpy(copy, str, len);
    }
    return copy;
}

// >> Reset reclaims memory without freeing blocks - use for batch operations
void pool_reset(MemoryPool *pool) {
    if (!pool) return;

    Block *block = pool->head;
    while (block) {
        block->used = 0;
        block = block->next;
    }
    pool->current = pool->head;
    pool->total_used = 0;
}

typedef struct PoolStats {
    size_t total_allocated;
    size_t total_used;
    size_t block_count;
    float utilization;
} PoolStats;

PoolStats pool_stats(const MemoryPool *pool) {
    PoolStats stats = {0};
    if (!pool) return stats;

    stats.total_allocated = pool->total_allocated;
    stats.total_used = pool->total_used;

    Block *block = pool->head;
    while (block) {
        stats.block_count++;
        block = block->next;
    }

    if (stats.total_allocated > 0) {
        stats.utilization = (float)stats.total_used / (float)stats.total_allocated;
    }

    return stats;
}

#ifdef POOL_TEST
#include <stdio.h>

int main(void) {
    MemoryPool *pool = pool_create(0);
    if (!pool) {
        fprintf(stderr, "Failed to create pool\n");
        return 1;
    }

    /* Allocate various sizes */
    int *nums = (int *)pool_alloc(pool, sizeof(int) * 100);
    char *str = pool_strdup(pool, "Hello, World!");
    double *data = (double *)pool_calloc(pool, 50, sizeof(double));

    for (int i = 0; i < 100; i++) {
        nums[i] = i * i;
    }

    printf("String: %s\n", str);
    printf("nums[10] = %d\n", nums[10]);

    PoolStats stats = pool_stats(pool);
    printf("Pool stats:\n");
    printf("  Allocated: %zu bytes\n", stats.total_allocated);
    printf("  Used: %zu bytes\n", stats.total_used);
    printf("  Blocks: %zu\n", stats.block_count);
    printf("  Utilization: %.1f%%\n", stats.utilization * 100);

    pool_destroy(pool);
    return 0;
}
#endif
