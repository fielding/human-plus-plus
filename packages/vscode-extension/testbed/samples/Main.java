// Human++ Java sample — annotations, generics, streams
import java.util.*;

@interface Note { String value(); }

public class Main {
  record User(int id, String name) {}

  @Note("HUMAN_HIGHLIGHT")
  static Optional<User> find(List<User> users, int id) {
    return users.stream().filter(u -> u.id() == id).findFirst();
  }

  public static void main(String[] args) {
    var users = List.of(new User(1, "Fielding"), new User(2, "Alex"));
    var name = find(users, 2).map(User::name).orElse("—");
    System.out.println("name=" + name);
  }
}
