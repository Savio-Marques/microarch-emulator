# Emulador de Microarquitetura UFC2X (Baseado em MIC-1)

Este projeto implementa um simulador completo de computador a nível de microarquitetura, fortemente inspirado na arquitetura **MIC-1** (desenvolvida por Andrew S. Tanenbaum em *Organização Estruturada de Computadores*). O sistema simula desde o clock de hardware, memória RAM de 1 MB de forma endereçável por byte e por palavra, até o caminho de dados de uma CPU com controle microprogramado (firmware) e um montador (*assembler*) personalizado.

---

## 📂 Estrutura do Projeto

O projeto é dividido nos seguintes componentes:

1. **`computador.py`**: O arquivo de entrada principal. Lê uma imagem de binário do disco virtual, carrega na memória virtual e inicia o sinal de clock para a CPU.
2. **`clock.py`**: Simula o sinal de clock do processador. O clock chama o ciclo de instrução de cada periférico/dispositivo acoplado a cada ciclo (*tick*) e encerra quando o processador entra em estado de parada (*halt*).
3. **`disk.py`**: Representa a unidade de armazenamento persistente. Lê o arquivo binário compilado pelo montador e o escreve byte a byte na memória RAM começando no endereço `0`.
4. **`memory.py`**: Simula uma memória RAM de 1 MB (composta por $262.144$ palavras de 32 bits). Oferece suporte tanto a leituras/escritas alinhadas por palavras (de 32 bits) quanto acessos individuais a bytes (formato *little-endian*).
5. **`ufc2x.py`**: O processador virtual (CPU). Contém a definição dos registradores de controle e de uso geral, barramentos internos (`BUS_A`, `BUS_B` e `BUS_C`), a lógica da ULA (Unidade Lógica e Aritmética) e a tabela de controle microprogramado (firmware) de 512 palavras.
6. **`assembler.py`**: O montador responsável por traduzir programas em linguagem assembly customizada (`.asm`) em binários executáveis (`.bin`). Ele faz a validação de instruções, o mapeamento de labels e o ajuste de endereçamento relativo a bytes ou a palavras de 32 bits.

---

## 🏛️ Arquitetura de Hardware (CPU & Memória)

### Registradores Internos da CPU (`ufc2x.py`)
- **`MPC`** *(Microprogram Counter)*: Ponteiro para a próxima microinstrução no firmware.
- **`MIR`** *(Microinstruction Register)*: Armazena a microinstrução atualmente em execução.
- **`PC`** *(Program Counter)*: Aponta para o endereço do próximo byte da instrução de máquina na memória RAM.
- **`MAR`** *(Memory Address Register)*: Registrador de endereço de memória para acesso a palavras.
- **`MDR`** *(Memory Data Register)*: Registrador de dados de memória para acesso a palavras.
- **`MBR`** *(Memory Buffer Register)*: Registrador de 8 bits que recebe dados de leitura de byte na memória (usado para leitura de opcodes e operandos imediatos).
- **`X`**: Registrador acumulador de uso geral para operações aritméticas.
- **`Y`**: Registrador auxiliar (presente na arquitetura, mas não utilizado nas instruções principais).
- **`H`** *(Holding Register)*: Registrador de retenção que alimenta sempre a entrada **`BUS_A`** da ULA.
- **`N`** e **`Z`**: Flags de estado da ULA indicando se o resultado foi Negativo (`N`) ou Zero (`Z`).

### Barramentos
- **`BUS_A`**: Conectado diretamente à saída do registrador `H`.
- **`BUS_B`**: Conectado à saída de um registrador selecionável (`MDR`, `PC`, `MBR`, `X` ou `Y`), controlado pelo campo `read_reg` da microinstrução.
- **`BUS_C`**: Transporta a saída da ULA de volta para gravação em um ou mais registradores de destino.

### Barramento de Memória RAM (`memory.py`)
A memória de 1 MB armazena inteiros de 32 bits representados em *little-endian*.
- **Leitura de Byte (`read_byte`)**: Usada para ler código (instruções e operandos). Mapeia o endereço de byte para a palavra correspondente na RAM e extrai os 8 bits corretos aplicando deslocamento.
- **Acessos de Palavra (`read_word`/`write_word`)**: Utilizam endereçamento indexado por palavras diretamente no vetor da memória RAM (ou seja, `read_word(1)` acessa os bytes do endereço físico `4` ao `7`).

---

## ⚙️ Formato das Microinstruções e Controle

Cada microinstrução do firmware possui 32 bits e é gerada pela função auxiliar `ucode` em `ufc2x.py`:
```python
def ucode(nxt, jam, alu_ctrl, shift, write_reg, mem_io, read_reg):
    return (nxt << 23) | (jam << 20) | (shift << 18) | (alu_ctrl << 12) | (write_reg << 6) | (mem_io << 3) | read_reg
```

### Campos da Microinstrução:
1. **`nxt`** (9 bits, bits 23-31): Endereço base da próxima microinstrução.
2. **`jam`** (3 bits, bits 20-22): Controle de saltos condicionais do microprograma.
   - `0b001` (JAMZ): Se a flag $Z == 1$, faz $MPC = nxt \lor 0x100$ (salto condicional se zero).
   - `0b010` (JAMN): Se a flag $N == 1$, faz $MPC = nxt \lor 0x100$ (salto condicional se negativo).
   - `0b100` (JMPC): Faz $MPC = nxt \lor MBR$, utilizado para desviar o microprograma diretamente para o endereço correspondente ao opcode da instrução lida.
3. **`shift`** (2 bits, bits 18-19): Operações de deslocamento na saída da ULA:
   - `0b01`: Deslocamento para a esquerda por 1 bit (`SLL1`).
   - `0b10`: Deslocamento para a direita por 1 bit (`SRL1`).
   - `0b11`: Deslocamento para a esquerda por 8 bits (`SLL8`).
4. **`alu_ctrl`** (6 bits, bits 12-17): Define a operação matemática/lógica realizada pela ULA.
5. **`write_reg`** (6 bits, bits 6-11): Sinais de escrita paralela nos registradores a partir do `BUS_C` (MAR, MDR, PC, X, Y, H).
6. **`mem_io`** (3 bits, bits 3-5): Controla operações de memória:
   - Bit 0 (`0b001`): Lê byte na memória no endereço apontado por `PC` e guarda no `MBR`.
   - Bit 1 (`0b010`): Lê palavra da memória no endereço apontado por `MAR` e guarda no `MDR`.
   - Bit 2 (`0b100`): Escreve palavra de `MDR` na memória no endereço apontado por `MAR`.
7. **`read_reg`** (3 bits, bits 0-2): Define qual registrador enviará seu dado para o `BUS_B`:
   - `0`: `MDR` | `1`: `PC` | `2`: `MBR` | `3`: `X` | `4`: `Y` | Outros: `0`.

---

## 🛠️ Conjunto de Instruções (ISA)

A tabela abaixo descreve as instruções de máquina suportadas pelo processador, seus opcodes hexadecimais correspondentes, parâmetros e seus comportamentos:

| Instrução | Opcode Hex | Parâmetros | Descrição |
| :--- | :--- | :--- | :--- |
| **`add`** | `0x02` | `x, label` | Soma o conteúdo da palavra de memória na posição `label` ao registrador `X` (`X = X + mem[label]`). |
| **`sub`** | `0x0D` | `x, label` | Subtrai o conteúdo da palavra de memória na posição `label` de `X` (`X = X - mem[label]`). |
| **`mul`** | `0x10` | `x, label` | Multiplica o registrador `X` pelo valor contido na memória (`X = X * mem[label]`) via hardware de multiplicação (`hw_mul`). |
| **`div`** | `0x11` | `x, label` | Divisão inteira de `X` pelo valor contido na memória (`X = X // mem[label]`) via hardware (`bit_divmod`). |
| **`mod`** | `0x12` | `x, label` | Resto da divisão de `X` pelo valor contido na memória (`X = X % mem[label]`) via hardware (`bit_divmod`). |
| **`load`** | `0x13` | `x, label` | Carrega o conteúdo da palavra na posição `label` de memória no registrador `X` (`X = mem[label]`). |
| **`store`** | `0x06` | `x, label` | Salva o conteúdo do registrador `X` na palavra de memória na posição `label`. |
| **`mov`** | `0x06` | `x, label` | Sinônimo de `store` (mesmo opcode `0x06`). |
| **`goto`** | `0x09` | `label` | Desvio incondicional para o endereço de byte apontado por `label`. |
| **`jz`** | `0x0B` | `x, label` | Desvio condicional para o endereço apontado por `label` caso a flag Zero `Z` esteja ativa (ou seja, `X == 0`). |
| **`jn`** | `0x0A` | `x, label` | Desvio condicional para o endereço apontado por `label` caso a flag Negativo `N` esteja ativa (ou seja, `X < 0`). |
| **`halt`** | `0xFF` | (nenhum) | Para a execução da CPU. |

### Pseudo-Instruções do Montador:
- **`wb <val>`** *(Write Byte)*: Escreve um valor constante de 1 byte (0 a 255) diretamente na imagem binária. Usado frequentemente para alinhamento.
- **`ww <val>`** *(Write Word)*: Escreve um inteiro constante de 4 bytes (32 bits, little-endian) na imagem binária. Usado para inicializar dados/variáveis na memória RAM.

---

## 🧭 Lógica de Execução e Alinhamento de Memória

### Ciclo de Instrução Fetch-Decode-Execute:
1. No início da execução, a CPU começa com `PC = 0` e `MPC = 0`.
2. A microinstrução no endereço `firmware[0]` realiza o incremento de `PC` para `1`, lê o byte correspondente ao opcode na memória no endereço `PC` antigo e joga no registrador `MBR`, executando em seguida um salto `JMPC` para `MPC = MBR` (endereço do opcode da instrução).
3. A partir daí, o microprograma específico do opcode assume o controle, operando os acessos à memória necessários e aplicando os cálculos através da ULA.
4. Ao final da rotina do opcode, o fluxo do microprograma volta sempre para a posição `0`, reiniciando o ciclo de busca de instrução.

### Alinhamento de Dados
Uma característica importante desta arquitetura é que as instruções de desvio (`goto`, `jz`, `jn`) funcionam operando com **endereços de byte** do binário. Já as instruções que operam com palavras de 32 bits (`load`, `store`, `add`, `sub`, etc.) utilizam **endereços de palavra** (endereço de byte dividido por 4).

Por esse motivo, o binário sempre inicia com um byte de preenchimento (`0`) no índice zero para que a primeira instrução útil comece no byte `1`. Logo depois da primeira instrução (geralmente `goto main`), é inserido uma diretiva `wb 0` de preenchimento. Isso garante que a área de variáveis de dados, declarada imediatamente a seguir com `ww`, esteja perfeitamente alinhada em um endereço múltiplo de 4 bytes (e, portanto, represente um índice inteiro simples no array da memória RAM).

---

## 📈 Programas de Teste Incluídos (`real1.asm` a `real4.asm`)

Os arquivos `.asm` contidos no diretório demonstram diferentes algoritmos aritméticos rodando diretamente sobre o emulador:

### 1. `real1.asm` (Soma de Divisores de um Número)
- **Descrição**: Lê um número inteiro em `in1` (inicializado com `42`). Determina se o número é par ou ímpar.
- **Comportamento**: Se for par, aplica uma lógica de fatoração rápida para calcular a soma de todos os seus divisores próprios e armazena o resultado em `out`.

### 2. `real2.asm` (Teste de Primalidade e Operações Adicionais)
- **Descrição**: Testa se o inteiro em `in1` é primo.
- **Comportamento**:
  - Se for **primo**, calcula a soma de todos os divisores de `in1 + 1` e guarda a soma em `out`.
  - Se **não for primo**, encontra o menor número primo estritamente maior que `in1` e escreve este número primo em `out`.

### 3. `real3.asm` (Produto Escalar de Vetores Empacotados)
- **Descrição**: Considere dois inteiros de 32 bits (`in1` e `in2`) como vetores empacotados de 4 componentes de 8 bits cada (bytes).
- **Comportamento**: Extrai os bytes correspondentes (através de operações sucessivas de `mod 256` e `div 256`), calcula o produto escalar termo a termo ($\sum a_i \times b_i$ para $i=0..3$) e guarda a soma resultante em `out`.

### 4. `real4.asm` (Rede de Ordenação de Bytes)
- **Descrição**: Desempacota os quatro bytes de um inteiro de 32 bits fornecido em `in1`.
- **Comportamento**: Ordena esses 4 bytes em ordem crescente através de uma rede de ordenação de 5 comparadores com trocas condicionais (baseados em desvios condicionais `jn` e lógica de *swap*). Ao final, reempacota os bytes ordenados (do mais significativo ao menos significativo) em um único valor de 32 bits e salva-o em `out`.

---

## 🚀 Como Executar o Emulador

### Requisitos
- Python 3.x instalado.

### Passo 1: Compilar o arquivo Assembly (`.asm`)
Use o script `assembler.py` passando o código-fonte assembly e o arquivo binário de saída desejado.

```bash
python assembler.py real1.asm real1.bin
```

### Passo 2: Executar o Binário no Computador Virtual
Use o script `computador.py` passando o binário compilado.

```bash
python computador.py real1.bin
```

O computador virtual imprimirá no console:
- O valor da variável `out` (geralmente na posição de memória `1` ou `220`) antes e depois da execução.
- O número de ciclos de clock (ticks) que o programa levou para concluir a execução.
