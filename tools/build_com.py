#!/usr/bin/env python3
"""Generate the gatti.sindro.me root (IT) pages from the gattibonsai.COM mirror (2001-02).

Texts copied verbatim from /com/*.htm (the most recent .com captures); every
@gattibonsai address becomes gatti@sindro.me. Successor of build.py (.it base).
"""
import hashlib, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from keepbrowsing import block as keep_browsing

OUT = sys.argv[1]
MAIL = "gatti@sindro.me"
CSS_V = hashlib.sha256(open(os.path.join(OUT, "css", "gatti.css"), "rb").read()).hexdigest()[:8]
AR = "https://web.archive.org/web/"
COM = "http://www.gattibonsai.com:80/"
ARCH = {
    "index": AR + "20010718020955/" + COM,
    "news": AR + "20011008060535/" + COM + "news.htm",
    "metodo": AR + "20010826012448/" + COM + "metodo.htm",
    "galleria": AR + "20010826012019/" + COM + "galleria.htm",
    "guest": AR + "20011008052634/" + COM + "guestbook.htm",
    "store": AR + "20010826012432/" + COM + "store.htm",
    "acc": AR + "20020105120519/" + COM + "acc.htm",
    "cont": AR + "20020105120531/" + COM + "cont.htm",
    "faq": AR + "20011008053418/" + COM + "faq.htm",
    "lavoro": AR + "20020206063227/" + COM + "lavoro.htm",
    "licia": AR + "20011008113401/" + COM + "licia.htm",
    "storia/chiuso": AR + "20010925200929/http://www.gattibonsai.it:80/",
    "storia/trasferito": AR + "20030129053921/http://www.gattibonsai.it:80/",
}
NAV = [("metodo", "Metodo"), ("store", "Store"), ("galleria", "Galleria"), ("guest", "Guestbook"), ("news", "News")]
# "Continua" chain, vjt's order (2026-10-19); galleria hangs off store
CHAIN = [("metodo", "Metodo"), ("store", "Store"), ("guest", "Guestbook"), ("news", "News"),
         ("faq", "F.A.Q."), ("lavoro", "Lavoro"), ("licia", "Bonsailicia")]
EXTRA = [("galleria", "Galleria")]
PARENT = {"acc": "store", "cont": "store", "galleria": "store"}
DISCLAIMER = ("Questo sito non è in alcun modo affiliato coi vicentini mangiagatti. Noi i gatti non li mangiamo "
              "e non li potiamo (o almeno non più). La nostra è una forma d'arte. Questo sito è Open Source. "
              "Puoi farne tutto quello che vuoi. Copiarlo, riciclarlo, mangiarlo, potarlo. Basta che non lo fai per soldi.")


def banner(page, up):
    base = "gattibonsai.it (2001)" if page.startswith("storia/") else "gattibonsai.com (2001&ndash;02)"
    return (
        f'<div class="bufala">Mirror archivistico di {base} &mdash; bufala satirica &laquo;Bonsai Kitten&raquo; '
        '(MIT 2000), nessun gatto maltrattato / satirical hoax, no cats harmed. '
        f'&middot; <a href="{ARCH[page]}">archive.org</a> '
        '&middot; <a href="/com/">.com</a> '
        '&middot; <a href="/2001/">.it giu 2001</a> '
        '&middot; <a href="/2001/v1/index.html">mar 2001</a> '
        f'&middot; <a href="{up}storia/chiuso.html">chiuso</a> '
        f'&middot; <a href="{up}storia/trasferito.html">trasferito</a> '
        '&middot; <a href="/2000/">English</a></div>'
    )


# Client-side language pick, root index only (see build.py).
LANG_REDIRECT = ("<script>try{if(!localStorage.getItem('lang')&&!/bot|crawl|spider|slurp|preview/i.test(navigator.userAgent)){"
                 "var l=(navigator.languages&&navigator.languages[0])||navigator.language||'it';"
                 "if(!/^it(-|$)/i.test(l))location.replace('/en/')}}catch(e){}</script>\n")
ALTERNATE = ('<link rel="alternate" hreflang="it" href="https://gatti.sindro.me/">\n'
             '<link rel="alternate" hreflang="en" href="https://gatti.sindro.me/en/">\n')


def head(title, up, extra=""):
    return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
{extra}<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#000000">
<link rel="stylesheet" href="{up}css/gatti.css?v={CSS_V}">
<script>document.documentElement.className+=' js'</script>
<script src="{up}js/gatti.js" defer></script>
</head>
"""


def page(name, body, wide=False):
    items = "\n".join(
        f'<li><a href="{p}.html"{" aria-current=\"page\"" if p == name else ""}>{label}</a></li>' for p, label in NAV
    )
    extra = LANG_REDIRECT + ALTERNATE if name == "index" else ""
    html = head("Gatti Bonsai - L'Arte.", "", extra) + f"""<body>
<header class="masthead">
<img class="kitten" src="lb.jpg" width="144" height="108" alt="">
<div class="brand">
<a href="index.html"><img src="logo-com.gif" width="179" height="43" alt="Gatti Bonsai.com"></a>
<p class="tagline">L'antica arte della plasmazione degli animali domestici</p>
</div>
<img class="kitten" src="lb.jpg" width="144" height="108" alt="">
</header>
<nav class="topnav" aria-label="Sezioni">
<div class="inner">
<a class="mini" href="index.html"><img src="logo-com.gif" width="179" height="43" alt=""></a>
<button class="burger" type="button" aria-expanded="false" aria-controls="navlist" aria-label="Menu"><span></span><span></span><span></span></button>
<ul id="navlist">
{items}
<li class="lang" data-nodiff><a href="/en/" lang="en" hreflang="en" data-lang="en">English</a></li>
</ul>
</div>
</nav>
<main{' class="wide"' if wide else ''}>
{body.strip()}
{keep_browsing("it", CHAIN, name, lambda k: k + ".html", parent=PARENT.get(name), home=("index", "Home"), extra=EXTRA)}
</main>
<footer>
<p class="disclaimer">{DISCLAIMER}</p>
{banner(name, "")}
</footer>
</body>
</html>
"""
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html)


def storia(name, title, body):
    html = head(title, "../") + f"""<body class="storia">
<header class="masthead">
<div class="brand"><a href="../index.html"><img src="../logo.gif" width="179" height="43" alt="Gatti Bonsai.it"></a></div>
</header>
<main>
{body.strip()}
{keep_browsing("it", CHAIN, name, lambda k: "../" + k + ".html", home=("index", "Home"), extra=EXTRA)}
</main>
<footer>
{banner(name, "../")}
</footer>
</body>
</html>
"""
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html)


def item(code, desc, imgs, flag=None):
    if flag and code:
        c = f'{code} <span class="flag">{flag}</span>'
    elif flag:
        c = f'<span class="flag">{flag}</span>'
    else:
        c = code
    pics = "".join(f'<a href="grandi/{i}" data-lb><img src="grandi/{i}" alt="" loading="lazy"></a>' for i in imgs)
    return f"""<article class="item">
<div class="pics">{pics}</div>
<div class="txt">
<p class="code">{c}</p>
<p class="desc">{desc}</p>
</div>
</article>"""


def catalog(cls, title, hint, items):
    return f"""<section class="catalog {cls}">
<div class="head">
<span class="codlabel">Cod. Art.</span>
<h2>{title}</h2>
<span class="hint">{hint}</span>
</div>
<div class="grid">
{chr(10).join(items)}
</div>
</section>"""


def news(date, title, paras, foot):
    ps = "\n".join(f"<p>{p}</p>" for p in paras)
    return f"""<article class="card news">
<header>
<p class="date">{date}</p>
<p class="title">{title}</p>
</header>
<div class="body">
{ps}
</div>
<footer>
<p>{foot}</p>
</footer>
</article>"""


M = f'<a href="mailto:{MAIL}">{MAIL}</a>'

# ------------------------------------------------------------------ index  (com/index.html)
page("index", f"""
<p class="lead center"><b><a href="news.html">Aggiornata sezione NEWS!!</a></b></p>
<section class="card">
<h2>Introduzione…</h2>
<p class="lead">Finalmente è giunta anche in Italia la moda che sta conquistando il mondo. I gatti in bottiglia. I gatti bonsai. Animali plasmati a nostro piacere. Per secoli gli occidentali hanno fantasticato pensando alle pregevoli produzioni dell'arte orientale. Dal giardinaggio ai tatuaggi, dalla danza alle arti marziali. La perfezione. Movimenti e forme sinuose. Forse la più affascinante delle tecniche visuali nata da questa cultura è l'arte orientale delle miniature. Chi non è rimasto sbalordito, a bocca aperta, davanti ad un bonsai giapponese? I bonsai sono superati. Ormai sono disponibili a poco prezzo in tutto il mondo. Con un occhio al passato, alla tradizione, e uno al futuro, all'innovazione, siamo orgogliosi di essere riusciti a portare anche in Italia la versione vivente, animale, di questa forma d'arte: il gatto bonsai.</p>
</section>
<section class="card split">
<img class="deco" src="bonsai.gif" width="170" height="200" alt="">
<div>
<h2>Principi di base…</h2>
<p>Piante bonsai e curatissimi giardini orientali miniaturizzati, raggiungono la loro forma migliore dopo anni e anni di cure e dopo un lungo e difficile processo di potatura durante la crescita delle piante stesse. Ovviamente non è possibile potare un gatto. Ci abbiamo provato. Non è stato piacevole. Soprattutto per il gatto. In ogni caso, i geniali artisti orientali, hanno trovato una tecnica per modificare la forma dell'animale mantenendolo in vita. Sia la fasciatura dei piedi che della testa furono praticate nel lontano oriente, con lo scopo di miniaturizzare le suddette parti del corpo del felino. Questa tecnica è alla base del nuovo metodo, detto "del corsetto", che sta diventando sempre più famosa in questi anni. Forzando fisicamente la crescita di una forma di vita si può fargli acquisire la forma del vaso che la contiene. Questo crea forme di vita uniche. Non sarete più obbligati ad avere per casa il solito, noiosissimo gatto che gira per casa. Avrete un animale unico, diverso da tutti gli altri. L'unico limite è la tua immaginazione. Se puoi immaginarlo puoi farlo.</p>
</div>
</section>
<section class="card center">
<p class="lead"><b>Curioso? Leggi le nostre <a href="faq.html">F.A.Q.</a></b></p>
<p class="lead"><b><a href="lavoro.html">Cerchi lavoro?</a></b></p>
<p>{M}</p>
</section>
""")

# ------------------------------------------------------------------ news  (com/news.htm)
page("news", "\n".join([
    news("01 Agosto 2001", "Inserite le FAQ!",
         ["Abbiamo inserito le FAQ sui GattiniBonsai!!"],
         '<a href="faq.html">Vai alla pagina delle FAQ!</a>'),
    news("30 Luglio 2001", "Vogliamo Te!!",
         ["In previsione della quotazione della nostra società sul Nuovo Mercato Telematico di Milano (NUMTEL), siamo in cerca di nuovo personale!",
          "Segui il link qua sotto per leggere gli annunci!"],
         '<a href="lavoro.html">Vai alla pagina del lavoro!</a>'),
    news("17 Luglio 2001", "Idiozia bionda",
         ["Sembra che una nota donna bionda in cerca di pubblicità, sapendola dare via, sia riuscita a censurare il nostro sito con la complicità della Polizia Italiana. Se vi dovesse interessare sappiate che il nome del magistrato genio che ha firmato il decreto è Adelchi D'Ippolito.",
          "Siamo di nuovo on line, più attivi di prima e con tanta voglia di fare e imbottigliare ma, come al solito, non di potare!!"],
         'Clicca qui per vedere <a href="licia.html">LICIABONSAI!</a>'),
    news("15 Luglio 2001", "Siamo una .COM Company!!",
         ["Gattibonsai si evolve! Ora siamo una .COM Company e puntiamo alla quotazione sul Nuovo Mercato Telematico di Milano!",
          "<i>&quot;L'Italia è un mercato fertile per i Gattibonsai, siamo molto felici di essere sbarcati nella vostra splendida penisola. Il clima sopraffino e l'abbondanza di materia prima rendono il vostro paese ideale per la nostra arte&quot;</i>",
          'Così ha commentato Alex Wuh, responsabile internazionale di <a href="/2000/">Bonsaikitten</a>, la nostra casa madre'],
         M),
    news("18 Aprile 2001", "Rieccoci finalmente!",
         ["Dopo qualche giorno di attesa dovuto alla migrazione del server siamo di nuovo con voi! Abbiamo rinnovato il sito dal punto di vista tecnico e in breve saranno aperte nuove sezioni! Facci sapere cosa ne pensi!"],
         M),
]))

# ------------------------------------------------------------------ store  (com/store.htm)
page("store", f"""
<h1>Commercio elettronico</h1>
<p class="lead">Ovviamente non abbiamo un catalogo di gatti già pronti. Ogni gatto bonsai è
arte, è unico e originale! Noi plasmiamo i gatti a vostro piacimento. L'esempio
più evidente del materiale che commerciamo, sono i vasi di varie forme, dalle
quali trarre ispirazione per plasmare i cuccioli. L'unica eccezione è che
talvolta plasmiamo degli animali che, per qualche ragione, non vengono spediti
al cliente che li aveva ordinati. Offriremo questi gatti al pubblico,
annunciandone la disponibilità sul nostro sito Internet. Il tempo necessario
per plasmare un gatto varia dai quattro ai sei mesi. Se avete già un cucciolo e
volete che noi lo plasmiamo, accettiamo, a volte, che voi ce lo spediate.
Ovviamente questo tipo di ordine è soggetto alla nostra valutazione. Bisogna
tenere conto dell'età del gatto, della razza e della distanza per la
spedizione. In ogni caso Gatti Bonsai.it non è responsabile per perdite o danni
durante le spedizioni di tali animali.</p>
<p>Oltre ai gatti plasmati, Gatti Bonsai.it è orgoglioso di poter offrire,
finalmente anche in Italia, una grande varietà di contenitori e di accessori
per chi vuole dilettarsi a casa propria:</p>
<div class="cols">
<section class="card">
<h3><a href="cont.html">Tipi di contenitori:</a></h3>
<ul>
<li>Vasi rettilinei</li>
<li>Urne e contenitori curvi</li>
<li>Costrizioni tubolari</li>
<li>Vasi a forma di animali antagonisti</li>
<li>Telai in rete metallica</li>
</ul>
</section>
<section class="card">
<h3><a href="acc.html">Accessori:</a></h3>
<ul>
<li>Calzascarpe</li>
<li>Sondini</li>
<li>Agenti elimina calcio</li>
<li>Rilassanti muscolari</li>
<li>Colle speciali</li>
</ul>
</section>
</div>
<p>Se Vi serve qualcosa che non abbiamo, <a href="mailto:{MAIL}">scriveteci</a>
e proveremo a trovarlo per Voi!</p>
<h2 class="blink">Rifornimenti da Gatti Bonsai.it</h2>
<p>Le pagine seguenti mostrano alcuni dei nostri prodotti disponibili per gli
hobbysti:</p>
<ul class="supply">
<li><a href="cont.html">Un assortimento dei nostri vasi preferiti</a></li>
<li><a href="acc.html">Accessori specialistici difficili da reperire</a></li>
</ul>
""")

# ------------------------------------------------------------------ metodo  (com/metodo.htm)
page("metodo", f"""
<h1>Metodo</h1>
<p class="lead">A poche settimane di vita, la struttura ossea dei gatti non ha ancora subito
quel processo di calcificazione che li renderebbe non più adatti al nostro
scopo. Le loro ossa sono estremamente morbide ed elastiche. E' conoscenza comune
che un gattino di poche settimane, se scaraventato con forza sul pavimento,
rimbalzi. Ovviamente vi sconsigliamo di provare tale pratica. Il piccolo micio
potrebbe finire sotto ad un mobile ed essere difficilmente recuperabile, oppure
potrebbe rimbalzare in qualche angolo sporco di casa e riempirsi di polvere. La
flessibilità ossea di questi cuccioli ci permette, se inseriti in tenera età
in appositi contenitori, di plasmarne a piacimento la forma. Noi di Gatti
Bonsai.it raggiungiamo questo scopo inserendo i gattini in contenitori rigidi
(preferibilmente di vetro) pochi giorni dopo la nascita, e liberandoli solamente
quando il loro processo di crescita sarà concluso e avranno raggiunto la forma
che tanto ci piaceva. I gattini crescono seguendo la forma del contenitore. Una
volta concluso questo complesso processo il gatto viene estratto (o il
contenitore rotto). Ci troveremo così tra le mani quella meravigliosa creatura
che abbiamo sempre desiderato nella forma da noi scelta. Non c'è virtualmente
limite alla forma che un gatto può assumere.</p>
<h2>Considerazioni pratiche</h2>
<p>Noi di Gatti Bonsai.it ci prendiamo cura per Voi di tutti i più piccoli
dettagli e Vi spediamo un gatto meraviglioso, completamente plasmato nella forma
da voi scelta. In ogni caso, per le persone o le società che hanno fatto
richiesta e hanno ottenuto il visto dal Ministero Della Sanità (DM 156/00,
13/09/2000 e successivo DPR 1107/00), forniamo anche le procedure e il materiale
per chi vuole partire da zero. Quando si crea un Gatto Bonsai bisogna tenere
conto di tre requisiti fondamentali:</p>
<ol class="req">
<li><b>Aria.</b> Forse non bisognerebbe neanche dirlo, ma sareste sorpresi dal
sapere quante persone alle prime armi hanno inserito un cucciolo in un
contenitore e lo hanno trovato morto stecchito al mattino! Se il contenitore
è sigillato IL GATTO NON RESPIRA! Dovete fare dei buchi nel tappo prima di
chiuderlo! Per contenitori interamente di vetro raccomandiamo l'uso di una
punta di diamante.</li>
<li><b>Cibo e Acqua.</b> Se ne stiamo plasmando la testa (che è una delle
pratiche più suggestive e gratificanti), il gatto non sarà più in grado
di bere e mangiare. La soluzione più comune consiste nel fare un altro buco
nel contenitore, inserendo un tubo che parta dalla bocca del gatto, in modo
che sia possibile introdurre cibo liquido e acqua attraverso il tubo stesso.</li>
<li><b>Pulire la sporcizia.</b> Lasciato senza cure, il gatto riempirà presto
il suo vaso di feci ed urina, portandolo ad ammalarsi e, con ogni
probabilità, alla morte. La soluzione che noi raccomandiamo è quella di
sigillare l'ano dell'animale con la nostra &quot;Super colla a base
naturale&quot; (a tale proposito consultate la sezione dedicata al <a href="store.html">commercio
elettronico</a>) prima di inserirlo nel vaso. Facendo un terzo buco nel
contenitore potremo raccogliere le feci che saranno contenute in un
involucro creato dalla nostra colla, gonfiata come un palloncino.</li>
</ol>
<p>Se avete la licenza per creare i vostri gattini, non esitate a contattare il
nostro <a href="mailto:{MAIL}">esperto</a> che sarà lieto di
aiutarvi e <a href="mailto:{MAIL}">comunicateci</a> i vostri
risultati! Il nostro staff è sempre lieto di aiutarvi. Ricordatevi di non
intraprendere questa pratica senza avere la dovuta preparazione e la licenza! Vi
ricordiamo che in base al DPR 1107/00, allevare cuccioli in un vaso può essere
fatto SOLO dopo aver ricevuto un'apposita autorizzazione dalle autorità. Questo
è necessario per evitare tristi torture da parte di gente inesperta o
semplicemente sadica. Gatti Bonsai.it non si assume nessuna responsabilità per
i risultati di pratiche descritte su questo sito.</p>
""")

# ------------------------------------------------------------------ galleria  (com/galleria.htm)
page("galleria", f"""
<section class="card center">
<h2>Galleria</h2>
<p>Questa sezione è ancora in costruzione! Non vogliamo
mostrarvi opere di importazione! Qui vedrete solamente gattini made in
Italy!</p>
<p>Se hai un gatto bonsai carino e vuoi che il mondo intero
gioisca vedendolo <a href="mailto:{MAIL}">scrivici</a>!</p>
<p>Ricordati che il materiale inviatoci (gatti compresi ma
solo se non potati) non sarà restituito!</p>
<figure>
<a href="gall1.jpg" data-lb><img src="gall1.jpg" width="394" height="232" alt=""></a>
<figcaption>Ecco i nostri primi amici! Presto avrete loro notizie!</figcaption>
</figure>
</section>
""")

# ------------------------------------------------------------------ guest  (com/guestbook.htm)
page("guest", f"""
<section class="card center">
<h2>Guestbook</h2>
<p>La pagina del Guestbook è in attesa dei vostri
commenti! Non esitate! Spedite pure commenti, critiche, poesie d'amore,
lamenti, pianti, trote, salici, gatti e ogni altra cosa riusciate a fare
passare per il doppino del telefono a:</p>
<p class="lead">{M}</p>
<p>Questo sito non è in alcun modo affiliato a:</p>
<p><a href="http://www.bruzzi.com">http://www.bruzzi.com</a></p>
</section>
<section class="card">
<p><i>agiursi@nopay.it</i> : <b>Compliementi per il sito! Siete grandi! Continuate così!!</b></p>
<p><i>bimba@tin.it</i> : <b>Se non fosse per voi il mio micio bonsai sarebbe morto! Vi voglio troppo bene! SMACK!!</b></p>
<p><i>KissMeLicia</i> : <b>Trovo scandaloso che Licia &quot;Exibith&quot; Colò si sia fatta fotografare pollice in alto mentre consegna la denuncia alla polizia postale.</b></p>
<p><i>Salkaner</i> : <b>Non capisco perchè la gente si dia tanto da fare a mettere i gatti in bottiglia quando tutti sanno che il modo migliore per usare un gatto è quell o di legargli sulla schiena una fetta di pane imburrata (col lato imburrato verso l'esterno), collegarlo con un albero mobile ad un generatore elettrico, quindi lasciarlo cadere da una qualsiasi altezza.</b></p>
<p><i>Antonio@libero.it</i> : <b>Ho tentato di mettere il mio gatto in bottiglia ma sono riuscito a far entrare solo una zampa. Così gli ho messo una bottiglia per zampa ed ora va in giro con i trampoli!!!!</b></p>
<p><i>BonsaiKitten'sLovers</i> <b>: mah, non capisco perchè vi arrabbiate tanto... vedendo il bellissimo sito dei gatti bonsai mi è venuta l'idea e ci ho provato sul serio: un mio amico la cui gatta ha da poco avuto 3 gattini me li ha regalati (altrimenti avrebbe dovuto sopprimerli dato il fatto che ne ha già 4) e io ho messo in pratica (almeno ci ho provato) quanto descritto nel sito. Il primo gattino, sfortunatamente, è morto quasi subito: ho usato infatti una bottiglia che si è rivelata troppo piccola e inadatta all'operazione, e ho maldestramente spezzato il collo dell'animale nel tentativo un po' violento di infilarlo dentro. Allora ho preso una bottiglia maggiormente somigliante a quelle che si vedono sul sito e, armato di buona volontà, ho introdotto il secondo gattino. Dopo aver tappato la bottiglia (ho fatto dei buchi nel tappo - che è di sughero - per far respirare l'animale) si è presentato il problema di nutrire la bestiolina e di dargli da mangiare.<br>
I miei tentativi di introdurre del latte mediante una siringa si sono però rivelati fallimentari, in quanto l'animale, poco propenso a star dentro al vetro, non ne ha voluto sapere di mangiare. Inoltre anche questa seconda bottiglia era piuttosto piccola, e il gatto è morto soffocato nella notte. Peccato!<br>
Per cautelarmi dalla perdita del terzo ed ultimo gatto mi sono dunque proposto di osservare attentamente la bestia e di estrarla dal contenitore non appena questa avesse mostrato segni di soffocamento, visto che io voglio molto bene agli animali.<br>
Ho scelto con cura la bottiglia: questa non deve essere nè troppo piccola (il gatto soffoca in quanto dimenandosi preme il musetto contro il vetro) nè troppo grossa (altrimenti si vanifica il fine del bonsaikitten, che, lo ricordo ai più, è quello di conferire alle simpatiche bestioline la forma del contenitore che li ospita).<br>
Ho dunque approntato il terzo contenitore e vi ho introdotto il gatto: per due volte ho dovuto stappare la bottiglia e, aiutandomi con una bacchetta, spostare il gatto che nel suo divincolarsi si era pericolosamente portato in posizioni che lo avrebbero condotto in breve all'asfissia. Sono stati due giorni faticosi, ma il mio immenso amore per i gattini mi ha motivato ad osservare continuamente la bottiglia artistica per tenere sotto controllo il gatto contenutovi. Oggi siamo già al terzo giorno di vita del mio bellissimo bonsaikitten, e proprio mentre scrivo lo tengo qui di fianco al monitor e di tanto in tanto lo osservo; ormai felice nella sua nuova dimensione il gattino pare sorridere per la felicità. Datemi retta: un bonsaikitten è per tutta la vita. De Beers...</b></p>
</section>
""")

# ------------------------------------------------------------------ acc  (com/acc.htm)
HINT_A = "Clicca sull'immagine per ingrandirla!"
SCRIVETECI = f'<p class="center"><a href="mailto:{MAIL}">Scriveteci</a> per i prezzi e per le\nnostre offerte speciali!</p>'
page("acc", f"""
<h1>Accessori utili e forniture</h1>
{SCRIVETECI}
{catalog("c1", "Forniture:", HINT_A, [
    item("7128-09", "<b>Graffette</b>. Inossidabili. Ideali per chiudere piccole ferite senza l'uso di punti di sutura.", ["woundclips.jpg"]),
    item("7128-10", "<b>Ciccatrizzatore</b>. Ideale per piccole ferite. Può essere iniettato sotto pelle.", ["syringetrio.jpg"], "SHORT!"),
    item("7128-12", "<b>Disinfettante</b> dai poteri cicatrizzanti. Ottimo per non rovinare il pelo.", ["superglueduo.jpg"]),
    item("7128-13", "<b>Pastiglie rilassanti</b>. Ideali per i momenti più critici. Due ogni pasto.", ["gauzeduo.jpg"]),
    item("7128-15", "<b>Kit per endovenose</b>. Versatile. Aghi intercambiabili.", ["iv.jpg"]),
    item("7128-16", "<b>Colla Vegetale</b> per sigillare orifizi. Ideale per l'ano.", ["epoxy.jpg"]),
])}
{catalog("c2", "Accessori:", HINT_A, [
    item("6312-64", '<b>&quot;Calzascarpe&quot;</b>. Ideali per mettere o togliere animali dai vasetti. Da <a href="http://www.alessi.it">Alessi</a> con amore.', ["alessi.jpg"]),
    item("6312-65", "<b>Speculum</b>. Illuminato. Ottimo per i lavori di precisione.", ["speculum.jpg"]),
    item("6312-67", "<b>Dosatore elettronico</b>. Basta riempire il serbatoio interno e grazie al lungo ago sarà possibile praticare ogni tipo di iniezione.", ["dosimeter.jpg"], "SHORT!"),
])}
{catalog("c3", "Equipaggiamenti:", HINT_A, [
    item("1522-01", "<b>Pompa</b>. Ideale per pompare aria o rimuovere rifiuti dai contenitori.", ["pump.jpg"]),
    item("1522-03", "<b>Sistemi di trazione automatizzati</b>. Protesi da applicare ai felini per pianificare torsioni e movimenti automatizzati. Possibilità di pianificare movimenti su più di un animale in contemporanea grazie al radiocomando incluso nella confezione.", ["tractor1.jpg", "tractor2.jpg"]),
])}
<p class="back"><a href="store.html">Torna alla pagina del commercio elettronico</a></p>
""", wide=True)

# ------------------------------------------------------------------ cont  (com/cont.htm)
page("cont", f"""
<h1>Vasi plasmanti</h1>
{SCRIVETECI}
{catalog("c1", "Per Principianti:", HINT_A, [
    item("1226-13", "<b>Cilindro in vetro</b> con speciale coperchio. Ideale per i principianti. Il coperchio include anche i fori per l'aerazione.", ["cylinderglass.jpg"]),
    item("1226-14", "<b>Scatola di plastica</b>. Permette la sperimentazione di fori ad un costo ridotto.", ["rectboxplastic.jpg"]),
    item("1226-17", f'<b>Scatola in vetro</b> con buchi già pronti. Può essere acquistata con o senza buchi. Per informazioni <a href="mailto:{MAIL}">scriveteci</a>.', ["rectboxglass.jpg"]),
])}
{catalog("c2", "Forme Curve:", HINT_A, [
    item("2236-29", "<b>Vaso cupolare</b>. Utile per far assumere alla testa del gatto una forma orientaleggiante.", ["dome.jpg"]),
    item("2236-32", "<b>Vaso sferico</b>. Richiede grande abilità per evitare avvolgimenti.", ["sphere.jpg"]),
    item("2236-37", "<b>Cilindro Germanico</b>. Ottimo contenitore che include un interessante spazio per la coda. Molto usato in Germania e Austria.", ["tubepip.jpg"]),
    item("2236-38", "<b>Cilindro conico</b>. Può essere usato in entrambe le direzione. Molto interessante ma può risultare complicato.", ["tubecone.jpg"]),
])}
{catalog("c3", "Avanzati:", HINT_A, [
    item("3114-47", '<b>Vaso per la fusione della coda</b>.<br>\nVaso di Klein per ottenere effetti unici. Si consiglia di leggerne il <a href="http://riemann.unica.it/geometria/grafmat/surfs5-f.html">manuale.</a>', ["advanced.jpg"]),
    item("3112-48", "<b>Vaso a forma canina</b>. Interamente in plastica. Di grande effetto.", ["dogplastic.jpg"], "SHORT!"),
    item("3112-50", "<b>Gabbia in metallo</b>. Usabile senza bisogno di tubi.", ["blackbands.jpg"]),
    item(None, "<b>La gabbia</b>. Particolare forma detta &quot;trappola per topi&quot;. Produce un fantastico effetto sulla superficie del gatto.", ["silverwire.jpg"], "ESAURITO!"),
])}
<p class="back"><a href="store.html">Torna alla pagina del commercio elettronico</a></p>
""", wide=True)

# ------------------------------------------------------------------ faq  (com/faq.htm)
FAQ = [
    ("Ho due gatti troppo grandi per il mio appartamento. Vorrei tanto ridurli. Vendete qualche prodotto che possa servire per il mio scopo?",
     "No. Sfortunatamente la tecnica dei gattibonsai è applicabile solo a gattini appena nati."),
    ("Ho allevato e formato il mio gattino bonsai in Italia. Mi sto trasferendo in Sud Africa, avrò dei problemi?",
     "No. L'effetto di Corioli non influisce sui Gattibonsai."),
    ("Il mio condominio vieta di tenere cani e gatti in casa. E' possibile praticare la tecnica della plasmazione degli animali domestici sugli orsi?",
     "No. Solo i gatti posseggono la struttura ossea adatta."),
    ("Sono un contadino di Piacenza. Vorrei allevare mucche bonsai. Potete aiutarmi?",
     "No. Le mucche non sono plasmabili a causa della loro struttura ossea."),
    ("Potete inviarmi un gatto bonsai via email?",
     "No. Le tecnologie attuali non lo permettono."),
    ("Qual'è il tasso di sopravvivenza di un gatto bonsai?",
     "Se allevato seguendo le nostre indicazioni, la mortalità e la vita media sono le stesse di un gatto normale."),
    ("E' vero che il gatto è meglio del coniglio?",
     "Sì. Il gatto è meglio del coniglio ma bisogna saperlo cucinare."),
]
page("faq", f"""
<h1>F.A.Q.</h1>
<p class="lead center"><b>Risposte alle domande più frequenti</b></p>
{chr(10).join(f'<section class="card center"><p><i>{q}</i></p>\n<p><b>{a}</b></p></section>' for q, a in FAQ)}
<section class="card center">
<p class="lead"><b><u>Hai domande da porci? Falle ai maiali!</u></b></p>
<p class="lead"><b>Hai domande per noi? <a href="mailto:{MAIL}">Scrivici!!</a></b></p>
</section>
""")

# ------------------------------------------------------------------ lavoro  (com/lavoro.htm)
page("lavoro", f"""
<h1>Abbiamo bisogno anche di te! La New Economy ti aspetta!</h1>
<section class="card">
<p class="lead center"><b>Cerchiamo giovani diplomati o laureati, con tanta voglia di
fare e di emergere. Ecco un elenco delle attitudini richieste:</b></p>
<p><b>- Capacità di lavorare in team<br>
- Ottima conoscenza della lingua inglese<br>
- Conoscenza della lingua cinese (non obbligatorio, costituirà titolo
preferenziale)<br>
- Disponibile a brevi trasferte in paese orientali (Cina e Giappone soprattutto
ma anche Corea e Vietnam)</b></p>
<p class="center"><b>Costituirà titolo preferenziale l'aver maturato precedenti
esperienze nella plasmazione degli animali domestici (soprattutto gatti in
bottiglie di vetro)</b></p>
<p class="center"><b>Se vuoi essere dei nostri
<a href="mailto:{MAIL}">contattaci</a>, inviando il tuo cv e
l'autorizzazione per il trattamento dei dati personali ai sensi della legge
675/96 e successive modificazioni. Verranno contattate solamente le persone
ritenute idonee.</b></p>
</section>
""")

# ------------------------------------------------------------------ licia  (com/licia.htm)
page("licia", """
<h1>BONSAILICIA</h1>
<section class="card">
<p>Lo sapevate? La nota
conduttrice televisiva Licia Colò si è adoperata per far chiudere il sito <b><a href="/2001/">www.gattibonsai.it</a></b>,
ispirato al più noto <b><a href="/2000/">www.bonsaikitten.com</a></b>, nel quale, tramite evidenti trucchi di
fotoritocco, si spiega come far crescere un gatto all'interno di una piccola
bottiglia, al fine di fargli assumere la forma e le dimensioni desiderate.<br>
Lo scherzo, magari di dubbio gusto, è palesemente evidente, e peraltro
neanche <i>Vulvia</i> di RIEDUCATIONAL CHANNEL avrebbe mai osato pensare che
si potesse far venir su un gatto di forma parallelepipeidale (si dirà così)
semplicemente mettendolo in una bottiglia da piccolo.<br>
Le mie ipotesi erano pertanto tre:</p>
<ol>
<li>Licia Colò è molto meno intelligente di Vulvia (..ed ancor meno i
poliziotti postali che si sono adoperati per far chiudere il sito)</li>
<li>Licia Colò pensa sul serio che ci sia gente che, ispirata da un sito
palesemente demenziale, inizi ad infilare gente e oggetti nelle bottiglie</li>
<li>Licia Colò era in cerca di pubblicità, per motivi suoi</li>
</ol>
<p>Spesso la verità però è più complessa della teoria... ed in effetti le tre
ipotesi erano tutte vere... e ne ho le prove... osservate queste immagini,
ottenute forzando il firewall (per i meno esperti: entrando nel computer)
della Rai TV, nella zona riservata al programma della Colò (non so come si
chiami ma ha a che fare con gli animali)</p>
</section>
<div class="cols">
<figure><a href="licia1.jpg" data-lb><img src="licia1.jpg" width="329" height="399" alt=""></a></figure>
<figure><a href="licia2.jpg" data-lb><img src="licia2.jpg" width="299" height="376" alt=""></a></figure>
</div>
<section class="card">
<p>Da queste immagini si evince
chiaramente che:</p>
<ol>
<li>Licia Colò è molto meno intelligente di Vulvia, visto che senza motivo
va in giro ad infilarsi nelle bottiglie (gli ampi sorrisi la confermano
consenziente)</li>
<li>Licia Colò pensa davvero che ci sia gente che va in giro ad infilare
cose nelle bottiglie, dal momento che ella stessa ha infilato in bottiglie
ella stessa</li>
<li>Licia Colò era in cerca di pubblicità, visto che ha parlato di
&quot;torture su poveri gattini&quot;, pur sapendo com'è divertente e piacevole
essere ficcato in una bottiglia</li>
</ol>
<p>Questo resti per i posteri, che non si facciano travolgere dalle campagne di
ipocrisia e perbenismo.</p>
<p><i>P.S.</i>: ...ah, le immagini sono taroccate, è tutto uno scherzo, per
favore nessuno, prendendo esempio da questo pazzo furioso (cioè io), vada ad
infilare Licia Colò in una bottiglia, come se fosse un messaggio o un
vascello</p>
</section>
<p class="lead center"><b>Si ringrazia <a href="http://www.belluomo.com">BELLUOMO.COM</a> per questa pagina</b></p>
""")

# ------------------------------------------------------------------ storia (.it only, unchanged texts)
os.makedirs(os.path.join(OUT, "storia"), exist_ok=True)
storia("storia/chiuso", "Questo sito è stato chiuso dalla Polizia Postale e delle Comunicazioni", """
<div class="stamp"><p class="big">Questo sito è stato chiuso <br>
dalla Polizia Postale e delle Comunicazioni</p></div>
""")
storia("storia/trasferito", "Questo sito si trova ora su", f"""
<p><a href="http://www.gattibonsai.com"><img src="../gattibonsai_banner_big.gif" width="468" height="60" alt=""></a></p>
<p class="big">Questo sito si trova ora su:</p>
<p class="url"><a href="http://www.gattibonsai.com">http://www.gattibonsai.com</a></p>
<p>Nulla è contenuto su questo server. Cliccando sul link qui sopra verrai
rediretto su un server statunitense di cui l'owner e webmaster di questo dominio
non si assume nessuna responsabilità in quanto non è né direttamente né
indirettamente a conoscenza di chi, come, quando, dove, perché, eccheccazzo, si
occupi di tale dominio .com. In ogni caso l'accesso a tale dominio è
sconsigliato ai minorenni, ai minorati, alle donne (bionde) e ai poveri di
spirito. Se clicchi su quel link sono solo cazzi tuoi. W i gattibonsai.</p>
<p class="alert"><span class="t">ATTENZIONE!</span>
Comunicazione da
<a href="mailto:{MAIL}">{MAIL}</a></p>
<p class="lead">La signora Colò ha organizzato una belle festa
per l'anniversario del suo sito (pubblicizzato per altro con la censura di
questo sito). Se qualcuno passa da Roma perché non ci fa un salto a farle sapere
cosa pensa Internet di questi atteggiamenti censori da pseudo vip? Come dice
l'invito riportato qui sotto... siete tutti invitati!</p>
""")
