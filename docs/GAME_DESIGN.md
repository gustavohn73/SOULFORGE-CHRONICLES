# Game Design Document - Soulforge Chronicles

## Visão Geral

**Gênero**: Roguelike Multiplayer com Narrativa Emergente

**Premissa**: Você está preso em um loop temporal. Cada ação que você toma marca sua alma de forma permanente. Quando a estabilidade do mundo chega a zero, uma IA analisa todas as ações dos jogadores e decide como o loop termina - redenção, condenação, ou algo pior.

## Conceitos Core

### 1. Sistema de Marcas (Soul Marks)

Cada ação do jogador afeta 4 marcas fundamentais:

#### VIOLÊNCIA (-100 a +100)
**Aumenta com:**
- Matar NPCs/jogadores
- Destruir objetos
- Usar armas de alto dano
- Escolher diálogos agressivos

**Efeitos Positivos (>50):**
- +15% dano
- +10% chance crítica
- Habilidades de combate desbloqueadas

**Efeitos Negativos (>80):**
- Mercadores recusam vender
- NPCs pacíficos fogem
- Guardas atacam on sight
- Marcado como "Assassino"

**Habilidade Desbloqueada (80+):**
- **Fúria Berserker**: +100% dano, -50% defesa por 5 turnos

#### CONTROLE (-100 a +100)
**Aumenta com:**
- Planejar rotas eficientes
- Organizar inventário
- Seguir leis/regras
- Usar estratégia em combate

**Efeitos Positivos (>50):**
- Dano consistente (baixa variância)
- +20% defesa
- Redução de cooldown de skills

**Efeitos Negativos (>80):**
- Loot reduzido (muito seletivo)
- NPCs te acham "chato"
- Menos eventos aleatórios

**Habilidade Desbloqueada (80+):**
- **Tempo Congelado**: Congela inimigos em 5 tiles por 2 turnos

#### CURIOSIDADE (-100 a +100)
**Aumenta com:**
- Explorar áreas novas
- Abrir baús/portas
- Ler livros
- Experimentar combinações de items

**Efeitos Positivos (>50):**
- +3 tiles de visão (FOV)
- Revela portas secretas
- +20% chance de loot raro

**Efeitos Negativos (>80):**
- Ativa armadilhas com mais frequência
- NPCs te testam com charadas
- Alguns NPCs te consideram "intrometido"

**Habilidade Desbloqueada (80+):**
- **Sexto Sentido**: Revela todos itens ocultos em 10 tiles

#### MEMÓRIA (-100 a +100)
**Aumenta com:**
- Completar loops
- Encontrar "fragmentos de memória"
- Revisitar locais de loops passados

**Efeitos Positivos (>50):**
- Lembra mapas de loops anteriores
- NPCs lembram de você
- Acesso a "Déjà Vu Points" (pontos de save mental)

**Efeitos Negativos (>80):**
- Sanidade diminui (-1 HP/turno em loops longos)
- Vê "fantasmas" de você mesmo
- Alguns NPCs te acham "assustador"

**Habilidade Desbloqueada (80+):**
- **Déjà Vu**: Volta 1 turno no tempo (cooldown: 200 turnos)

### 2. Loop Temporal

#### Estrutura de um Loop

1. **Início (Stability: 100%)**
   - Todos jogadores spawnam juntos em "Hub Town"
   - Tempo no relógio: 15-60 minutos (aleatório)
   - GM anuncia tema do loop (ex: "Fome infinita", "Noite eterna")

2. **Exploração (Stability: 100-50%)**
   - Jogadores exploram dungeons procedurais
   - Coletam recursos, matam inimigos
   - Marcas mudam baseado em ações
   - GM registra eventos importantes

3. **Tensão (Stability: 50-20%)**
   - Clima piora (chuva → tempestade → apocalíptica)
   - Inimigos mais fortes aparecem
   - Eventos caóticos aumentam
   - Jogadores devem decidir: cooperar ou trair?

4. **Final (Stability: 0%)**
   - Contador chega a zero
   - GM analisa todas as ações do loop
   - Gera final único baseado nas marcas coletivas
   - Loop reseta, marcas persistem

#### Tipos de Finais (Gerados por IA)

**Final Redentor (Marcas balanceadas):**
- Jogadores acordam em um mundo melhor
- Bonus de XP permanente
- Novo item único aparece na próxima run

**Final Violento (VIOLÊNCIA coletiva >60):**
- Boss final: "Encarnação da Fúria"
- Derrotar = grande recompensa
- Perder = perde todo loot

**Final Caótico (CONTROLE coletivo <-60):**
- Mundo vira completo caos
- Física do jogo muda (gravidade, cores)
- Sobreviver 5 minutos = vitória

**Final Curioso (CURIOSIDADE coletiva >70):**
- Portal para "Biblioteca Infinita" abre
- Dentro: perguntas filosóficas
- Respostas corretas = conhecimento proibido

**Final Memória (MEMÓRIA coletiva >80):**
- Jogadores veem todos os loops passados simultaneamente
- Podem escolher "salvar" um momento do passado
- Isso muda o presente permanentemente

### 3. Multiplayer Assíncrono

#### Como Funciona

- **Lobby Compartilhado**: Até 10 jogadores por loop
- **Drop-in/Drop-out**: Pode entrar/sair a qualquer momento
- **Cooperação Opcional**: Não é obrigatório se agrupar
- **PvP Habilitado**: Pode atacar outros jogadores, mas:
  - Aumenta VIOLÊNCIA drasticamente
  - Marca você como "Traidor" (ícone vermelho no mapa)
  - NPCs te tratam como vilão

#### Comunicação

- **Chat de Texto**: Padrão
- **Pings no Mapa**: Marcar locais importantes
- **Emotes**: 10 animações (acenar, apontar, etc)

### 4. Fog of War Individual

Cada jogador vê apenas:
- Área ao redor dele (visão baseada em stats)
- Jogadores próximos (mesmo fora do FOV, aparecem no mapa)
- Áreas já exploradas (cinza escuro, sem inimigos visíveis)

Inimigos só aparecem quando:
- Dentro do seu FOV, OU
- Fazendo barulho alto (combate)

### 5. Combate

#### Sistema Base (roubado de Shattered Pixel Dungeon)

**Turno a turno em tempo real:**
- Cada ação (mover, atacar, item) consome "ticks"
- Jogador rápido (Agilidade alta) = mais ações por segundo
- Inimigo lento = menos ações

**Cálculo de Dano:**
```
base_damage = random(arma_min, arma_max) + bonus_level
modificador_marca = (VIOLÊNCIA - 50) / 200
dano_final = (base_damage * (1 + modificador_marca)) - defesa_inimigo
```

**Críticos:**
- 5% chance base
- +10% se VIOLÊNCIA > 50
- Crítico = 2x dano

**Surpresa:**
- Se atacar inimigo que não te vê (fora do FOV dele)
- +50% dano
- Ataque garantido (não pode errar)

#### Armas

| Arma | Min | Max | Tier | Especial |
|------|-----|-----|------|----------|
| Punhos | 1 | 3 | 0 | Sempre disponível |
| Adaga | 3 | 8 | 1 | +20% crit backstab |
| Espada | 6 | 15 | 2 | Balanceada |
| Machado | 10 | 25 | 3 | Alta variância |
| Lança | 8 | 18 | 2 | +2 alcance |
| Arco | 5 | 12 | 2 | Ataque ranged (5 tiles) |

#### Status Effects

- **Envenenado**: -2 HP/turno, 5 turnos
- **Queimando**: -3 HP/turno, 3 turnos, espalha para adjacentes
- **Congelado**: Não pode se mover, 2 turnos
- **Atordoado**: 50% chance de ação falhar, 2 turnos
- **Berserk**: +100% dano, -50% defesa, 5 turnos

### 6. Geração Procedural

#### Tipos de Dungeons

**Dungeon Clássico (ROT.js Digger):**
- Salas retangulares + corredores
- 8-15 salas
- Boss no final

**Caverna Orgânica (ROT.js Cellular):**
- Automata celular
- Sem salas definidas
- Inimigos em grupos

**Floresta Densa:**
- Tiles de árvore bloqueiam visão
- Muitas emboscadas
- Cogumelos com efeitos aleatórios

**Cidade em Ruínas:**
- Grid de ruas
- Casas saqueáveis
- NPCs sobreviventes

**Torre Ascendente:**
- Vertical (sobe andares)
- Cada andar = desafio temático
- Topo = boss final

### 7. NPCs Gerados por IA

#### Tipos

**Mercadores:**
- Personalidade gerada (ganancioso, generoso, medroso)
- Preços mudam baseado em suas marcas
- Se VIOLÊNCIA alta, pode te recusar

**Quest Givers:**
- Geram missões dinâmicas usando IA
- Exemplo: "Meu filho está preso na caverna do norte"
- Recompensa: Item único ou info sobre boss

**Companheiros:**
- Podem se juntar temporariamente
- Têm inventário próprio
- Podem trair você (IA decide baseado em suas ações)

**Facções:**
- 5 facções procedurais por loop
- Cada uma tem ideologia gerada (ex: "Culto do Fogo Eterno")
- Ganhar reputação desbloqueia quests exclusivos

### 8. Crafting

#### Receitas Base

| Item | Ingredientes | Tempo | Requer |
|------|--------------|-------|--------|
| Bandagem | 2x Pano | 5 turnos | Nada |
| Poção Cura | 1x Erva + 1x Água | 10 turnos | Alquimia |
| Espada Ferro | 3x Barra Ferro + 1x Madeira | 50 turnos | Forja |
| Flecha (x10) | 1x Madeira + 1x Pedra | 15 turnos | Nada |

#### Crafting Avançado (Sistema de Marcas)

**Fragmento de Alma:**
- Ingredientes: 1x Cristal + 5x Essência
- Custo: -10 MEMÓRIA (sacrifica memórias)
- Resultado: Item que armazena 1 habilidade
- Tempo: 100 turnos
- Requer: Altar da Forja de Almas

**Arma Amaldiçoada:**
- Ingredientes: 1x Arma qualquer + 1x Sangue Amaldiçoado
- Custo: +30 VIOLÊNCIA
- Resultado: Arma com +50% dano, mas -10 HP/minuto
- Tempo: 80 turnos
- Requer: Forja

### 9. Eventos Dinâmicos

Gerados pela IA GM Master a cada 5-10 minutos:

**Exemplos:**

**"Meteoro Caindo":**
- Anuncia em 60 segundos
- Marca no mapa onde vai cair
- Jogadores próximos tomam 50 dano
- Cria cratera com minério raro

**"Horda de Zumbis":**
- Spawna 20 inimigos fracos
- Convergem para posição de player com mais VIOLÊNCIA
- Derrotar todos = XP bonus

**"Comerciante Misterioso":**
- Aparece aleatoriamente
- Vende item único
- Desaparece após 2 minutos

**"Portal Instável":**
- Spawna portal
- Entrar = teleporta para dungeon aleatório
- Pode ser armadilha ou tesouro

**"Duelo de Honra":**
- IA desafia player com VIOLÊNCIA alta
- NPC elite aparece
- Se ganhar: item lendário
- Se perder: marca "Covarde"

### 10. Progressão

#### Experiência e Nível

- Matar inimigos = XP
- Completar loops = XP massivo
- Cada nível: +10 HP, +1 ponto de atributo

**Atributos:**
- **Força**: +2 dano por ponto
- **Agilidade**: +5% velocidade de movimento e ataque
- **Resistência**: +15 HP por ponto
- **Percepção**: +1 tile de visão a cada 3 pontos
- **Sorte**: +2% crit, +2% loot raro

#### Persistência Entre Loops

**Persiste:**
- Marcas (VIOLÊNCIA, CONTROLE, CURIOSIDADE, MEMÓRIA)
- Nível e XP
- Habilidades desbloqueadas
- 3 itens favoritos (marcados)
- Conhecimento de NPCs (alguns lembram de você)

**Reseta:**
- Inventário (exceto 3 favoritos)
- Posição no mapa
- Quests em andamento
- Mundo procedural (novo mapa)

## Pilares de Design

1. **Ações têm Consequências**: Cada escolha marca sua alma permanentemente
2. **Emergência Narrativa**: IA cria histórias únicas baseado em gameplay
3. **Cooperação > Competição**: Mas traição é possível e tentadora
4. **Morte não é Punição**: É narrativa (loop reseta, você evolui)
5. **Assimetria de Informação**: FOV cria tensão e surpresas

## Balanceamento

### Para Evitar

- **Violência Dominante**: Caminhos pacíficos devem ser viáveis
  - Solução: Mercadores recusam atender assassinos

- **Farming Infinito**: Loops têm tempo limite
  - Solução: Countdown forçado

- **Trolling**: Player mata todos outros
  - Solução: Marca "Traidor", NPCs todos hostis, spawn isolado

### Ciclos de Feedback

- **Positivo**: Marcas altas desbloqueiam skills poderosas
- **Negativo**: Marcas extremas (>80) têm desvantagens sociais

## Métricas de Sucesso

- **Retenção**: 60% dos jogadores voltam para 2º loop
- **Engajamento**: Sessão média de 30 minutos
- **Social**: 70% dos loops têm 3+ jogadores simultâneos
- **IA**: 80% dos finais são considerados "interessantes" pelos jogadores

## Referências

- **Shattered Pixel Dungeon**: Combate, FOV, items
- **Dark Souls**: Morte como mecânica, não punição
- **Cultist Simulator**: Timers visíveis, tensão temporal
- **AI Dungeon**: Narrativa gerada por IA
- **Outer Wilds**: Loop temporal como exploração
