#include <iostream>
#include "thread_pool.hpp"

std::mutex mutex_lock;

int task_fun(const std::vector<int>& input_vec, int i) {
  std::this_thread::sleep_for(std::chrono::seconds(1));
  ;
  mutex_lock.lock();
  std::cout << input_vec[i] << std::endl;
  mutex_lock.unlock();
  return 0;
}

int main() {
  std::vector<int> input_vec;
  for (int i = 0; i < 10; ++i) {
    input_vec.push_back(i);
  }

  ThreadPool thead_pool(4);

  for (int i = 0; i < 10; ++i) {
    thead_pool.submit(new Task(task_fun, std::ref(input_vec), i));
  }

  thead_pool.wait();

  return 0;
}
