# Como atualizar o site da TV Arena Esportes

Site: **tvarenaesportes.com.br** — um único arquivo, `index.html` (HTML + CSS + JS, sem build).
Tudo que vai para a branch `main` deste repositório é publicado automaticamente na Hostinger.

Público: leitores brasileiros. Todo texto em **português do Brasil**, tom jornalístico, direto,
sem cara de IA (nada de "No cenário atual...", "Vale ressaltar", listas de emoji).
Nome da marca: **TV Arena Esportes** (nunca "Sports"). Redação: São Paulo (SP),
e-mail tvarenaesportes@gmail.com. Direção de reportagem: Ruy Ávila, Andre Veras, João Marcelo.

## Rotina diária

1. `git pull` e leia este arquivo.
2. Pesquise na web o que aconteceu **desde a última atualização** (ontem e hoje) e o que vem **hoje/amanhã**:
   - Futebol: Brasileirão Série A e Série B (resultados, autores dos gols, público, estádio), Copa do Brasil,
     Libertadores/Sul-Americana, Seleção.
   - Vôlei (Superliga, seleção), Basquete (NBB, NBA com brasileiros), Lutas (UFC, brasileiros),
     Motor (F1, Stock Car), Tênis (ATP/WTA, João Fonseca e brasileiros).
   - Use pelo menos uma fonte confiável por fato e **cruze placar e autores de gol em duas fontes**.
     Nunca invente placar, gol, público ou declaração. Se não confirmar, não publique.
3. Atualize os dados no `index.html` (seção abaixo).
4. Rode `python3 tools/check.py`. Só siga se terminar com `OK`.
5. Faça commit (`Atualização diária DD/MM`) e `git push origin main`.
6. Termine com um resumo curto em português: matérias novas, placares atualizados, o que ficou pendente.

## Onde fica cada coisa no `index.html`

Procure pelos nomes abaixo (são variáveis JS dentro do `<script>` principal):

| O que | Onde | Formato |
|---|---|---|
| Data no topo | `<span id="today">` | JS já coloca a data do dia sozinho |
| Faixa "Plantão" (letreiro) | `<div class="ticker-track">` | links `<a href="#...">texto</a>`; troque pelas manchetes do dia |
| Matéria principal da home | `#materia` / `view-article` (HTML fixo) | título, linha fina, data, corpo, fontes |
| Placar do topo, por esporte | `var SCORES={futebol:[...],volei:[...],...}` | `{st:'ENCERRADO · SÉRIE A',end:1,rows:[['Time A','2'],['Time B','1']],href:'#jogo-id'}`; jogo futuro usa `'–'` e `st:'19H30 · SÉRIE B'` |
| Matérias de jogo do futebol | `var GAMES=[...]` | ver exemplo existente (`id`, `g:[casa,gols,fora,gols]`, `k`, `date`, `wd`, `venue`, `pub`, `goals`, `ctx`, `pts`, `src`) |
| Notas e matérias de todos os esportes | `var EXTRA=[...]` | `{id, teams:[slugs], sport, k, t, d, date, body:[parágrafos], src:[[nome,url]]}` |
| Resultados da temporada (Série A/B) | `var SEASON={"sa":[...],"sb":[...]}` | `[rodada,'dd/mm',casa,golsCasa,golsFora,fora]` |
| Tabela Série A / Série B | `var TAB_SA`, `var TAB_SB` | `[slug,pontos,jogos,vitórias,empates,derrotas,saldo]` |
| Próximos jogos (calendários) | `SA_FIX`, `SB_FIX` e blocos `calAdd(...)` logo abaixo de `var CAL={}` | quando um jogo acontecer, tire da lista de próximos e ponha o resultado em `SEASON` |
| F1 | `F1_PAST`, `F1_CAL`, `F1_DRV`, `F1_CON` | corridas feitas, calendário, pilotos, construtores |
| Tênis | `ATP` | ranking |
| Lutas | `var UFC=[...]` | lutadores por categoria |
| Outras equipes (vôlei, basquete, motor) | `var EQ={...}` | equipes/atletas e seus calendários |

Slugs dos clubes: veja `var TEAMS=[...]` (ex.: `flamengo`, `atletico-mg`, `sao-paulo`, `vila-nova`).
Um `id` novo em `GAMES`/`EXTRA` nunca pode repetir um existente.

Contagem de notícias por time e o mínimo de 3 matérias por time/atleta são calculados sozinhos pelo JS
(funções `allNewsFor`/`countNews` e as análises geradas em `AN`). Não mexa nisso.

## Regras

- Cada matéria nova: título informativo, linha fina, 3 a 6 parágrafos com números concretos, e `src` com as fontes reais (nome + URL).
- Não copie texto de outros sites; escreva com as próprias palavras e cite a fonte.
- Não use fotos externas (a política do site é arte SVG própria, já gerada automaticamente).
- Remova da home notícias com mais de ~5 dias (deixe-as em `EXTRA`/`GAMES`, só tire do destaque e do letreiro).
- Não mude layout, cores ou estrutura sem pedido do Ruy.
- Se algo der errado no `check.py` e você não conseguir corrigir, **não dê push**; relate o problema no resumo.

## Plantão de 2 em 2 horas (todos os clubes, equipes, atletas e lutadores)

Uma tarefa separada roda a cada 2 horas atrás de **notícias quentes de todos os esportes do site**:
os 40 clubes das Séries A e B, as equipes de vôlei, basquete e automobilismo, os lutadores e os tenistas.
Para ver os identificadores (slugs) de todos: `python3 tools/slugs.py` (ou `python3 tools/slugs.py lutas`).

1. `git pull --rebase` antes de começar e de novo antes do push (outra tarefa pode ter mexido no arquivo).
2. Pesquise o que saiu nas **últimas ~3 horas**: jogos/lutas/corridas, escalação, lesões, contratações e saídas confirmadas,
   decisões de diretoria, punições, anúncios de lutas, resultados, rankings, bastidores com veículo nomeado.
3. **Só publique se for realmente relevante e novo.** Antes, confira se o assunto já existe no site
   (procure no `index.html` por palavras-chave, títulos e URLs de fonte, e veja `git log`).
   Boato sem fonte séria não entra. **Se não houver nada bom, não altere nada e não faça commit.**
4. Onde entra: item novo **no topo** de `var PLANTAO=[` (a mais nova sempre em cima):
   ```js
   {id:'2609-1430-fla-lesao-arrascaeta', sp:'futebol', quem:['flamengo'],
    k:'Flamengo · Departamento médico', t:'Título informativo', d:'Linha fina com o dado principal',
    date:'26/09', hora:'14h30', body:['parágrafo 1','parágrafo 2', ...], src:[['ge','https://...'],['Lance','https://...']]},
   ```
   - `sp`: `futebol`, `volei`, `basquete`, `lutas`, `motor` ou `tenis`.
   - `quem`: slugs de quem a notícia trata. A matéria aparece na página de **cada um** deles **e** na aba do esporte.
     Ex.: clássico `quem:['flamengo','fluminense']`; luta `quem:['alexandre-pantoja']`.
   - Notícia do esporte que não é de nenhum clube/atleta do site (Seleção, CBF, arbitragem, outro evento): `quem:[]`
     → aparece só na aba do esporte.
   - `id` nunca pode repetir. Se for a notícia mais forte do momento, ponha também no letreiro "Plantão" (`ticker-track`).
   - A contagem de notícias de cada clube/equipe/atleta sobe sozinha.
5. **Padrão da matéria (obrigatório):** nada genérico. Mínimo de **5 parágrafos** com fatos concretos:
   o que aconteceu, quando e onde; nomes completos; números (placar, valores, prazos, minutos, estatísticas da temporada,
   cartel do lutador, posição no campeonato); declarações atribuídas a quem falou (com o veículo que publicou);
   contexto (tabela, sequência, histórico do confronto); e o que acontece a seguir (próximo jogo, prazo, decisão pendente).
   Pelo menos **2 fontes** diferentes em `src`. Proibido: frases vazias ("promete agitar", "a torcida está ansiosa"),
   opinião sem base, repetir a linha fina no corpo, texto que serviria para qualquer time.
6. `python3 tools/check.py` → só com `OK` faça commit (`Plantão DD/MM HHh: <assunto>`) e push.
   Pode publicar mais de uma matéria no mesmo plantão, se houver mais de um assunto realmente relevante.
