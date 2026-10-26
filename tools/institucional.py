"""Textos das páginas institucionais. Edite aqui e rode python3 tools/build_pages.py.

Cada entrada: slug -> (título, descrição para o Google, corpo em HTML).
"""

EMAIL = '<a href="mailto:tvarenaesportes@gmail.com">tvarenaesportes@gmail.com</a>'
ATUALIZADO = "14 de outubro de 2026"
CNPJ = "53.743.776/0001-68"

PAGES = {
"quem-somos": ("Quem somos",
"A TV Arena Esportes é um site de jornalismo esportivo independente, com redação em São Paulo (SP).",
f"""
<p>A TV Arena Esportes é um site de jornalismo esportivo independente, com redação em São Paulo (SP).
Cobrimos futebol (Brasileirão Séries A e B, Copa do Brasil, Libertadores, Sul-Americana e Seleção),
vôlei, basquete, lutas, automobilismo e tênis, com atenção especial aos clubes e atletas brasileiros.</p>

<h2>Como trabalhamos</h2>
<p>Publicamos notícia quando há fato novo e confirmado. Placar, autor de gol, público e declaração só entram
no site depois de conferidos em fontes confiáveis, e toda matéria traz, no fim, a lista das fontes consultadas,
com link. Não publicamos boato sem fonte identificada.</p>
<p>As matérias são escritas com palavras próprias da redação. Quando uma informação foi divulgada primeiro por
outro veículo, ele é citado no texto e nas fontes.</p>

<h2>Correções</h2>
<p>Errou, corrigimos. Se você encontrou um erro em alguma matéria, escreva para {EMAIL} com o link da página.
A correção é feita na própria matéria.</p>

<h2 id="expediente">Expediente</h2>
<ul>
<li>Direção de reportagem: Ruy Ávila, Andre Veras e João Marcelo</li>
<li>Redação: São Paulo (SP)</li>
<li>CNPJ: {CNPJ}</li>
<li>Contato: {EMAIL}</li>
</ul>
<p>Leia também a nossa <a href="/politica-de-privacidade/">Política de privacidade</a> e os
<a href="/termos-de-uso/">Termos de uso</a>.</p>
"""),

"contato": ("Contato",
"Fale com a redação da TV Arena Esportes: sugestões de pauta, correções, anúncios e parcerias.",
f"""
<p>O canal oficial de contato da TV Arena Esportes é o e-mail {EMAIL}. Respondemos em dias úteis.</p>
<ul>
<li><b>Sugestão de pauta ou informação:</b> conte o que aconteceu e, se puder, indique a fonte.</li>
<li><b>Correção:</b> envie o link da matéria e o trecho que precisa ser corrigido.</li>
<li><b>Anúncios e parcerias:</b> veja a página <a href="/anuncie/">Anuncie</a>.</li>
<li><b>Dados pessoais (LGPD):</b> pedidos de acesso, correção ou exclusão de dados seguem a
<a href="/politica-de-privacidade/">Política de privacidade</a>.</li>
</ul>
<p>Redação: São Paulo (SP).</p>
"""),

"anuncie": ("Anuncie",
"Anuncie na TV Arena Esportes: sua marca perto de quem acompanha futebol, vôlei, basquete, lutas, automobilismo e tênis.",
f"""
<p>A TV Arena Esportes publica notícias o dia inteiro sobre os 40 clubes das Séries A e B, além de vôlei,
basquete, lutas, automobilismo e tênis. Cada clube, equipe e atleta tem página própria, o que permite
anunciar para a torcida certa.</p>

<h2>Formatos</h2>
<ul>
<li><b>Banner no site:</b> na página inicial, nas editorias ou nas páginas de um clube específico.</li>
<li><b>Patrocínio de editoria ou de clube:</b> sua marca associada à cobertura de um esporte ou de um time.</li>
<li><b>Patrocínio do resumo diário no WhatsApp:</b> uma menção por dia no canal da TV Arena.</li>
<li><b>Conteúdo de marca:</b> sempre identificado como publicidade, separado do noticiário.</li>
</ul>

<h2>Regras</h2>
<p>Publicidade nunca se mistura com notícia e é sempre identificada como tal. Não aceitamos anúncio enganoso,
nem de produto ou serviço ilegal. Anúncios de apostas, se aceitos, seguem a legislação brasileira
(somente operadoras autorizadas, público maior de 18 anos e mensagens de jogo responsável).</p>

<h2>Fale com a gente</h2>
<p>Envie um e-mail para {EMAIL} com o assunto "Quero anunciar" e conte o que você precisa.
Enviamos formatos, audiência e valores.</p>
"""),

"politica-de-privacidade": ("Política de privacidade",
"Como a TV Arena Esportes trata dados pessoais e cookies, de acordo com a Lei Geral de Proteção de Dados (LGPD).",
f"""
<p><i>Última atualização: {ATUALIZADO}.</i></p>
<p>Esta política explica quais dados pessoais a TV Arena Esportes (tvarenaesportes.com.br) trata quando você
visita o site, para que eles são usados e quais são os seus direitos, de acordo com a Lei nº 13.709/2018
(Lei Geral de Proteção de Dados, LGPD).</p>

<h2>1. Quem é o responsável</h2>
<p>O controlador dos dados é a TV Arena Esportes, CNPJ {CNPJ}, com redação em São Paulo (SP). Para qualquer assunto
sobre dados pessoais, inclusive para falar com o encarregado, escreva para {EMAIL}.</p>

<h2>2. Quais dados tratamos</h2>
<ul>
<li><b>Dados de navegação:</b> endereço IP, tipo de navegador e de aparelho, páginas visitadas, data e hora
de acesso. Esses registros são gerados automaticamente pelo servidor de hospedagem e por serviços de terceiros
usados no site.</li>
<li><b>Dados que você nos envia:</b> nome, e-mail e o conteúdo da mensagem, quando você escreve para a redação.</li>
<li><b>Canal no WhatsApp:</b> ao entrar no canal, a relação é com o WhatsApp, sob as regras dele.
Seguidores de canais não têm o número de telefone exibido para o administrador.</li>
</ul>
<p>Não pedimos cadastro para ler o site e não coletamos dados sensíveis.</p>

<h2>3. Para que usamos</h2>
<ul>
<li>Manter o site no ar, seguro e funcionando (legítimo interesse);</li>
<li>Medir a audiência e entender quais conteúdos interessam aos leitores (legítimo interesse ou consentimento,
conforme o caso);</li>
<li>Exibir publicidade, que mantém o site gratuito (legítimo interesse ou consentimento, conforme o caso);</li>
<li>Responder mensagens enviadas à redação;</li>
<li>Cumprir obrigações legais, como a guarda de registros de acesso exigida pelo Marco Civil da Internet
(Lei nº 12.965/2014).</li>
</ul>

<h2>4. Cookies e publicidade</h2>
<p>Cookies são pequenos arquivos gravados no seu navegador. O site e os parceiros abaixo podem usá-los para
lembrar preferências, medir audiência e exibir anúncios.</p>
<ul>
<li>Fornecedores terceiros, incluindo o Google, usam cookies para exibir anúncios com base em visitas
anteriores do usuário a este e a outros sites.</li>
<li>Com os cookies de publicidade, o Google e os parceiros dele podem exibir anúncios com base nas visitas
feitas a este site e a outros sites na internet.</li>
<li>Você pode desativar a publicidade personalizada nas
<a href="https://adssettings.google.com" target="_blank" rel="noopener">Configurações de anúncios do Google</a>
e conhecer outras opções em <a href="https://www.aboutads.info/choices/" target="_blank" rel="noopener">aboutads.info</a>.
Saiba como o Google usa dados em
<a href="https://policies.google.com/technologies/partner-sites" target="_blank" rel="noopener">policies.google.com/technologies/partner-sites</a>.</li>
<li>Usamos o Google Analytics para medir a audiência (páginas visitadas, tempo de leitura, origem das visitas e tipo de aparelho), de forma agregada, sem identificar o leitor. Saiba mais e veja como desativar em
<a href="https://tools.google.com/dlpage/gaoptout" target="_blank" rel="noopener">tools.google.com/dlpage/gaoptout</a>.</li>
<li>O site carrega fontes do Google Fonts; para isso, o seu navegador informa o endereço IP ao Google.</li>
<li>Vídeos indicados no site abrem no YouTube, que segue a política de privacidade do Google.</li>
</ul>
<p>Você pode bloquear ou apagar cookies nas configurações do navegador. Algumas funções podem deixar de
funcionar, mas a leitura das notícias continua possível.</p>

<h2>5. Com quem compartilhamos</h2>
<p>Com prestadores necessários ao funcionamento do site: a empresa de hospedagem, serviços de medição de
audiência e redes de publicidade, como o Google. Não vendemos dados pessoais. Alguns desses parceiros podem
tratar dados fora do Brasil, com as garantias previstas na LGPD.</p>

<h2>6. Por quanto tempo guardamos</h2>
<p>Registros de acesso ao site são guardados por 6 meses, como exige o Marco Civil da Internet. Mensagens
enviadas à redação ficam guardadas pelo tempo necessário para responder e para eventual defesa em processos.
Cookies têm prazos próprios, definidos por quem os grava.</p>

<h2>7. Seus direitos</h2>
<p>Pela LGPD (art. 18), você pode pedir: confirmação de que tratamos seus dados; acesso; correção;
anonimização, bloqueio ou eliminação de dados desnecessários; portabilidade; informação sobre com quem
compartilhamos; e revogação do consentimento, quando ele for a base do tratamento. Basta escrever para
{EMAIL}. Você também pode reclamar à Autoridade Nacional de Proteção de Dados (ANPD).</p>

<h2>8. Crianças e adolescentes</h2>
<p>O site é de notícias para o público geral e não coleta, de forma intencional, dados de crianças.</p>

<h2>9. Mudanças nesta política</h2>
<p>Esta política pode ser atualizada. A data no início da página indica a versão em vigor.</p>
"""),

"termos-de-uso": ("Termos de uso",
"Regras de uso do site TV Arena Esportes: conteúdo, direitos autorais, links externos e responsabilidades.",
f"""
<p><i>Última atualização: {ATUALIZADO}.</i></p>
<p>O site tvarenaesportes.com.br pertence à TV Arena Esportes, CNPJ {CNPJ}.
Ao usar o site, você concorda com estes termos.</p>

<h2>1. Conteúdo</h2>
<p>A TV Arena Esportes publica notícias e informações esportivas com base em fontes indicadas em cada matéria.
Placares, tabelas e calendários são atualizados com frequência, mas datas e horários de jogos podem mudar por
decisão das entidades organizadoras. Para compromissos importantes, confira também a fonte oficial.</p>

<h2>2. Direitos autorais</h2>
<p>Textos, artes e o projeto gráfico do site pertencem à TV Arena Esportes (Lei nº 9.610/1998).
Você pode compartilhar o link de qualquer matéria. A reprodução de textos ou artes, total ou parcial,
depende de autorização por escrito e da citação da fonte. Marcas, nomes e escudos de clubes e competições
pertencem aos respectivos titulares e aparecem apenas para identificação jornalística.</p>

<h2>3. Links externos</h2>
<p>O site traz links para fontes, vídeos e serviços de terceiros. Não respondemos pelo conteúdo nem pelas
práticas de privacidade desses sites.</p>

<h2>4. Publicidade</h2>
<p>O site pode exibir anúncios de terceiros, sempre identificados. A responsabilidade pela oferta anunciada é do
anunciante. A presença de um anúncio não significa recomendação da redação.</p>

<h2>5. Uso adequado</h2>
<p>Não é permitido usar o site para fins ilegais, tentar acessar áreas restritas, sobrecarregar o servidor ou
copiar o conteúdo de forma automatizada para republicação.</p>

<h2>6. Privacidade</h2>
<p>O tratamento de dados pessoais segue a nossa <a href="/politica-de-privacidade/">Política de privacidade</a>.</p>

<h2>7. Lei aplicável e contato</h2>
<p>Estes termos seguem a legislação brasileira. Dúvidas: {EMAIL}.</p>
"""),
}
