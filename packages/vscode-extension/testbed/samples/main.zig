const std = @import("std");
const Allocator = std.mem.Allocator;

/// Configuration for the connection pool
const PoolConfig = struct {
    max_connections: u32 = 10,
    timeout_ms: u64 = 5000,
    retry_attempts: u32 = 3,
};

/// Represents a database connection
const Connection = struct {
    id: u64,
    created_at: i64,
    last_used: i64,
    in_use: bool,

    fn init(id: u64) Connection {
        const now = std.time.milliTimestamp();
        return .{
            .id = id,
            .created_at = now,
            .last_used = now,
            .in_use = false,
        };
    }

    fn markUsed(self: *Connection) void {
        self.last_used = std.time.milliTimestamp();
        self.in_use = true;
    }

    fn release(self: *Connection) void {
        self.in_use = false;
    }
};

/// Thread-safe connection pool
// !! Pool does not handle connection health checks - add ping before use
const ConnectionPool = struct {
    connections: std.ArrayList(Connection),
    config: PoolConfig,
    mutex: std.Thread.Mutex,
    allocator: Allocator,
    next_id: u64,

    fn init(allocator: Allocator, config: PoolConfig) ConnectionPool {
        return .{
            .connections = std.ArrayList(Connection).init(allocator),
            .config = config,
            .mutex = .{},
            .allocator = allocator,
            .next_id = 0,
        };
    }

    fn deinit(self: *ConnectionPool) void {
        self.connections.deinit();
    }

    fn acquire(self: *ConnectionPool) !*Connection {
        self.mutex.lock();
        defer self.mutex.unlock();

        // Try to find an available connection
        for (self.connections.items) |*conn| {
            if (!conn.in_use) {
                conn.markUsed();
                return conn;
            }
        }

        // Create new connection if under limit
        if (self.connections.items.len < self.config.max_connections) {
            const conn = Connection.init(self.next_id);
            self.next_id += 1;
            try self.connections.append(conn);
            const ptr = &self.connections.items[self.connections.items.len - 1];
            ptr.markUsed();
            return ptr;
        }

        return error.PoolExhausted;
    }

    fn releaseConn(self: *ConnectionPool, conn: *Connection) void {
        self.mutex.lock();
        defer self.mutex.unlock();
        conn.release();
    }

    // ?? Should we add automatic connection eviction for idle connections?
    fn getStats(self: *ConnectionPool) struct { total: usize, in_use: usize } {
        self.mutex.lock();
        defer self.mutex.unlock();

        var in_use: usize = 0;
        for (self.connections.items) |conn| {
            if (conn.in_use) in_use += 1;
        }

        return .{
            .total = self.connections.items.len,
            .in_use = in_use,
        };
    }
};

/// Execute a function with a pooled connection
fn withConnection(
    pool: *ConnectionPool,
    comptime func: fn (*Connection) anyerror!void,
) !void {
    const conn = try pool.acquire();
    defer pool.releaseConn(conn);
    try func(conn);
}

/// Query result row
const Row = struct {
    columns: []const []const u8,

    fn get(self: Row, index: usize) ?[]const u8 {
        if (index >= self.columns.len) return null;
        return self.columns[index];
    }
};

// >> All queries must go through this function for logging
fn executeQuery(conn: *Connection, query: []const u8) ![]Row {
    _ = conn;
    _ = query;
    // Placeholder implementation
    return &[_]Row{};
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    const config = PoolConfig{
        .max_connections = 5,
        .timeout_ms = 3000,
    };

    var pool = ConnectionPool.init(allocator, config);
    defer pool.deinit();

    // Acquire and use a connection
    const conn = try pool.acquire();
    defer pool.releaseConn(conn);

    std.debug.print("Connection {d} acquired\n", .{conn.id});

    const stats = pool.getStats();
    std.debug.print("Pool stats: {d} total, {d} in use\n", .{ stats.total, stats.in_use });
}

test "connection pool basics" {
    const allocator = std.testing.allocator;

    var pool = ConnectionPool.init(allocator, .{});
    defer pool.deinit();

    const conn1 = try pool.acquire();
    const conn2 = try pool.acquire();

    try std.testing.expect(conn1.id != conn2.id);
    try std.testing.expect(conn1.in_use);
    try std.testing.expect(conn2.in_use);

    pool.releaseConn(conn1);
    try std.testing.expect(!conn1.in_use);
}
