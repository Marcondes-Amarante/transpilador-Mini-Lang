#include <stdio.h>
#include <stdlib.h>

int calcular(/*params */);

int x;
int resultado;


int calcular(int n) {
    if ((n > 0)) {
        return (n * calcular((n - 1)));
    }
    return 1;
} 

int main() {
    int x = 5;
    int resultado = 1;
    printf(" Calculando Fatorial de 5:\n");
    resultado = calcular(x);
    printf("%d\n", resultado);
    return 0;
}