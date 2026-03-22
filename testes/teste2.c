#include <stdio.h>
#include <stdlib.h>

void verificar(/*params */);

float nota1;
int aprovado;
float x;


void verificar(int n) {
    if ((n <= 7)) {
        printf("Aprovado!\n");
    } else {
        printf("Reprovado.\n");
    }
} 

int main() {
    float nota1 = 8.5;
    int aprovado = 1;
    float x = 0;
    x = (10 + (5 * 2));
    return 0;
}