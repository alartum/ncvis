#include <cstdlib>
#include <stdio.h>
#include "ncvis.hpp"
#include "../lib/pcg-cpp/include/pcg_random.hpp"

int main(int argc, char** argv){
  if (argc < 6){
    std::cout << "Usage: ncvis [number of points] [number of neighbors] [number of threads] [maximum epochs] [number of init epochs]";
    return 1;
  }
  size_t N=atoi(argv[1]), D=28*28, d=2;
  size_t n_threads = atoi(argv[3]);
  float* X = new float[N*D];

  // pcg_extras::seed_seq_from<std::random_device> seed_source;
  pcg64 pcg(42);
  std::uniform_real_distribution<float> gen_X(0, 1);
  for (size_t i=0; i<N*D; ++i){
    X[i] = gen_X(pcg);
  }

  ncvis::NCVis vis(d, n_threads, atoi(argv[2]), 8, 200, 42, atoi(argv[4]), atoi(argv[5]));

  float* Y = vis.fit(X, N, D);
  if (Y == nullptr) return 1;

  // printf("-----------------\n");
  // for (size_t i=0; i<N; ++i){
  //   printf("[");
  //   for (size_t j=0; j<d; ++j){
  //     printf("%6.2lf ", Y[d*i+j]);
  //   }
  //   printf("]\n");
  // }
  // printf("-----------------\n");
  
  delete[] X;
  delete[] Y;
  return 0;
}