// Human++ C++ sample — templates, macros, raw strings
#include <iostream>
#include <string>
#include <vector>
#include <optional>

#define TODO(x) /* TODO(x) */

template <typename T>
std::optional<T> first(const std::vector<T>& v) {
  if (v.empty()) return std::nullopt;
  return v.front();
}

int main() {
  std::vector<std::string> v{"Fielding", "Alex"};
  auto x = first(v).value_or("—");
  std::cout << "x=" << x << "\n";

  const char* raw = R"(regex: (\w+)\s*=\s*(.+))";
  std::cout << raw << "\n";

  TODO(check-contrast);
  return 0;
}
