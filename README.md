# Progettone Master in Big Data \& Social Mining - Gruppo 5

## Struttura della repository

- analysis: in questa cartella vi sono le analisi salienti del progetto
    - Lyrics: analisi dei testi delle canzoni
    - Music: analisi dei brani musicali con _Deep Learning_
    - Timeseries: analisi delle metriche di Spotify nel tempo
    - Artists: script per creare il grafo delle collaborazioni
- data: in questa cartella vi erano i dati con i quali abbiamo fatto le varie analisi (ora è tutto su Drive)
    - check\_data\_utils: in questa cartella ci sono gli script usati per controllare la qualità del dataset e per pulire il dataset principale
- initial\_data\_gathering: script utilizzati per scaricare i dati
    - scraper: cartella con gli script degli scraper
        - fimi_scaper: scraper per le top chart della FIMI
        - genius: scraper per le lyrics di Genius
        - google: scaper accessorio per ottenere lyrics direttamente da google
        - music_brainz: wrapper per API di musicbrainz.org, un database di informazioni su artisti
    - spotify\_info: script usati per integrare i dati da Spotify
- altair\_notebooks: notebook utilizzati per generare le visualizzazioni con Altair

## Descrizione del dataset principale
Il dataset principale è denominato _combined\_df\_final.csv_.
È composto dalla lista di canzoni più ascoltate in italia da metà 2006 a metà 2021 secondo la FIMI, ha 64,794 righe e 34 colonne.

### Colonne
- original\_song\_name: nome della canzone sul sito della FIMI
- original\_artists\_name: nome degli artisti sul sito della FIMI
- curr\_rank: posizione in classifica
- tag\_fimi: tag del sito
- publisher: nome del publisher
- date\_chart: data della classifica
- album\_release\_date: data del rilascio della canzone
- album\_type: tipo di album
- song\_name: nome della canzone
- album\_id: id spotifyu dell'album
- artists\_names: nomi degli artisti formattati come una lista python
- artists\_id: id Spotify degli artisti formattati come una lista python
- explicit: se la canzone è esplicità
- duration: durata in secondi
- song\_id: id Spotify della canzone
- popularity: 0popolarità della canzone (metrica di Spotify)
- danceability: Quanto il brano è danzabile basato su una combinazione di elementi musicali tra cui il tempo, il ritmo, ecc. Da 0 a 1
- energy:  Rappresenta l’energia e l’intensità della canzone. Le canzoni più energetiche sono più veloci, rumorose, chiassose.
- key: tonalità della canzone
- loudness: Volume della canzone in decibels (dB)
- mode:
- speechiness: Presenza di parole in una canzone. Sotto lo 0.33 sono canzoni senza testo
- acousticness: la probabilità che una canzone sia acustica
- instrumentalness: Se una canzone ha parti cantate o meno. Il rap è il contrario della instrumentalness. Più alto è il valore e più la canzone non presenta parti cantate.
- liveness: probabilità di una canzone di essere live
- valence:  La positività o meno della canzone. Più alto è il valore e più il suono è positivo e cioè euforico, gioioso ecc...
- tempo: i BPM della canzone
- id: id spotify della canzone
- uri: Spotify uri della canzone
- track\_href: url spotify della canzone
- analysis\_url: url dell'analisi musicale della canzone'
- duration\_ms: durata della canzone
- time\_signature: armatura in chiave
