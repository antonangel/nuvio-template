# nuvio-template

A Nuvio + AIOMetadata setup as four importable files plus the art library they point at.
Everything here is a verbatim export of a working setup — nothing is generated, nothing is
scripted, nothing is built. Import a file, or take the art and host your own.

```
addons/    the four exports. import these.
assets/    the folder/collection art library, one dir per family
```

## The four files

| file | addon | what it is |
|---|---|---|
| `addons/aiometadata-collections.json` | AIOMetadata 3.2.3 | **main profile**: 351 catalogs, no streaming set, collections carried as catalogs |
| `addons/aiometadata-no-collections.json` | AIOMetadata 3.2.3 | **Friends profile**: 46 catalogs (27 on), collections come from the Nuvio file instead |
| `addons/nuvio-collections.json` | Nuvio client | the folder/collection layout: 6 top folders, 114 sub-folders, each wired to catalog sources |
| `addons/aiostreams.json` | AIOStreams | Tamtaro partial SEL 3.0.4 + Vidhin ranked regexes, usenet `cacheAndPlay` |

The two AIOMetadata files are **two different profiles, not two halves of one config** —
different catalog sets, different manager accounts, different defaults. Import the one you want.

## Importing

- `aiometadata-collections.json` / `aiometadata-no-collections.json` → AIOMetadata → **Import config**.
  This **replaces the whole config**, and carries no API keys — add your own TMDB/TVDB/etc. keys after.
- `nuvio-collections.json` → Nuvio client → **Import collections**, or AIO → Collections → Import collections.
- `aiostreams.json` → AIOStreams → **Import config**.

A collections file in the Catalogs dialog fails with *Invalid configuration file format*, and a
catalog export in the Collections dialog is rejected — one file per dialog.

## Credentials

Nothing here holds a working credential. Every `apiKeys` block is empty, both AIOStreams
`services[].credentials` are empty, and the TorBox key that the original exports carried inside the
Comet and StremThru preset URLs has been replaced with `REPLACE_WITH_YOUR_OWN_TORBOX_API_KEY`.
Substitute your own before importing, and expect the Comet/StremThru presets to fail until you do.

## Collections — what `nuvio-collections.json` builds

6 top folders, 114 sub-folders, each with `coverImageUrl` and its catalog `sources`.

**Discover** — 4 folders, `FOLLOW_LAYOUT` view

- Trending, Popular, Top, Latest

**Streaming Services** — 11 folders, `FOLLOW_LAYOUT` view

- Netflix, Disney+, Apple TV, Prime Video, HBO Max, Hulu, Paramount+, Peacock, Starz, Shudder, Adult Swim

**Genres** — 17 folders, `FOLLOW_LAYOUT` view

- Action, Comedy, Sci-Fi, Crime, Thriller, Drama, Horror, Mystery, Mindfuck, Anime, Documentary, Romance, History, Animation, Reality TV, Family, Nature

**Decades** — 6 folders, `FOLLOW_LAYOUT` view

- 20s Movies, 10s Movies, 00s Movies, 90s Movies, 80s Movies, 70s Movies

**Collections** — 70 folders, `FOLLOW_LAYOUT` view

- Marvel, DC Universe, Star Wars, James Bond, Harry Potter, Alien vs Predator, Pirates of the Caribbean, Terminator, Mission Impossible, Jurassic Park, The Matrix, Lord of the Rings, A Nightmare On Elm Street, A Quiet Place, Alien, American Pie, Are You Afraid Of The Dark, Avatar, Back To The Future, Bad Boys, Blair Witch, Bourne Collection, Candyman, Chucky, Dexter, Die Hard, Dune, Eberhofer Krimis, Expendables, Fast Furious, Final Destination, Friday The 13Th, Ghostbusters, Gremlins, Halloween, Hannibal Lecter, Happy Death Day, Hunger Games, Indiana Jones, It, John Wick, Jurassic World, Karate Kid, Kingsman, Mad Max, Monsterverse, Now You See Me, Oceans, Paranormal Activity, Planet Of The Apes, Police Academy, Predator, Psycho, Quarantine, Rambo, Resident Evil, Rocky, Saw, Scream, Sherlock Holmes, Star Trek, Taken, Terrifier, The Conjuring Universe, The Exorcist, The Godfather, The Purge, The Shining, Transformers, Xxx

**Awards** — 6 folders, `FOLLOW_LAYOUT` view

- BAFTA, Cannes, Emmy Awards, Golden Globes, Academy Awards, Venice Film Festival

Art comes from `assets/` (live exports hotlink the same filenames from public repos:
`itsitohere/nuvio-assets`, `illiyah/Images`, `itsrenoria/fusion-starter-kit`). Swap the URLs for
your own hosting if you fork this.

## Catalogs

### Main profile — `aiometadata-collections`

351 catalogs, 351 enabled. Sources: recommendations 2, mdblist 168, anilist 1, mal 2, tmdb 178.

- **recommendations** (2): For You (`recommendations.movies`, movie), For You (`recommendations.series`, series)
- **mdblist** (168): Popular 2020s Movies (movie), Popular 2010s Movies (movie), Popular 2000s Movies (movie), Popular 1990s Movies (movie), Popular 1980s Movies (movie), Popular 1970s Movies (movie), Popular 1960s Movies (movie), Popular Sci-Fi Movies (movie), Popular Sci-Fi Shows (series), Popular Action Movies (movie), Popular Action Shows (series), Popular Crime Movies (movie), Popular Crime Shows (series), Popular Comedy Movies (movie), Popular Comedy Shows (series), Popular Drama Movies (movie), Popular Drama Shows (series), Popular Horror Movies (movie), Popular Horror Shows (series), Popular Thriller Movies (movie), Popular Thriller Shows (series), Popular Mystery Movies (movie), Popular Mystery Shows (series), Popular History Movies (movie), History TV Shows (series), Popular Romance Movies (movie), Popular Romance Shows (series), Popular Reality Shows (series), Latest Nature Documentaries (series), Popular Documentary Movies (movie), Popular Documentary Shows (series), Popular Animated Movies (movie), Popular Animated Shows (series), Popular Family Movies (movie), Popular Family Shows (series), Mindfuck (movie), Adult Swim (series), Shudder Movies (movie), Shudder Series (series), James Bond Collection (movie), Harry Potter Collection (movie), Jurassic Park Collection (all), The Matrix Collection (movie), Pirates of the Caribbean Collection (movie), Lord of the Rings and Hobbit Collection (movie), Alien vs Predator Collection (all), The Terminator Collection (all), Mission Impossible Collection (movie), A Nightmare on Elm Street (movie), A Quiet Place Collection (movie), Alien (movie), American Pie (movie), Are You Afraid of the Dark? (movie), Avatar Collection (movie), Back to the future (movie), Bad Boys (movie), Blair Witch Collection (movie), Bourne Collection (movie), Candyman (movie), Chucky (movie), DC Universe (movie), Dexter (movie), Die Hard (movie), Dune (movie), Eberhofer-Krimis (movie), Expendables (movie), Fast and Furious Collection (movie), Final Destination (movie), Friday the 13th (movie), Ghostbusters (movie), Gremlins (movie), Halloween Collection (movie), Hannibal Lecter (movie), Happy Death Day Collection (movie), Hunger Games (movie), Indiana Jones (movie), It Collection (movie), John Wick (movie), Jurassic Park (movie), Karate Kid (movie), Kingsman (movie), Mad Max (movie), Marvel (movie), Monsterverse (movie), Now You See Me (movie), Ocean's Collection (movie), Paranormal Activity (movie), Planet of The Apes (movie), Police Academy (movie), Predator Collection (movie), Psycho (movie), Quarantine Collection (movie), Rambo (movie), Resident Evil (movie), Rocky (movie), Saw (movie), Scream (movie), Sherlock Holmes (movie), Star Trek (movie), Star Wars Collection (movie), Taken (movie), Universe - The Terminator (movie), Terrifier (movie), The Conjuring Universe (movie), The Exorcist (movie), The Godfather (movie), The Purge (movie), The Shining Collection (movie), Transformers (movie), xXx Collection (movie), BAFTA Award Nominees (movie), Cannes 2000 (movie), Cannes 2001 (movie), Cannes Film Festival - 2005 (movie), Cannes Film Festival - All Films (movie), Cannes Film Festival Non-Retro Screenings 1946-2025 (movie), Emmy Awards - Outstanding Comedy Series (series), Emmy Awards - Outstanding Drama Series (series), Emmy Awards - Outstanding Miniseries (movie), Emmy Nominees (series), Emmy Nominees and Winners (movie), Golden Globe Award: Animated Feature Film (movie), Golden Globe Award: Best Actor in a Motion Picture – Drama (movie), Golden Globe Award: Best Actor in a Motion Picture – Musical or Comedy (movie), Golden Globe Award: Best Actress in a Motion Picture – Drama (movie), Golden Globe Award: Best Actress in a Motion Picture – Musical or Comedy (movie), Golden Globe Award: Best Director – Motion Picture (movie), Golden Globe Award: Best Motion Picture - Drama (movie), Golden Globe Award: Best Motion Picture - Foreign Language (movie), Golden Globe Award: Best Motion Picture - Musical or Comedy (movie), Golden Globe Award: Best Original Score in a Motion Picture (movie), Golden Globe Award: Best Original Song in a Motion Picture (movie), Golden Globe Award: Best Screenplay in a Motion Picture (movie), Golden Globe Award: Best Supporting Actor in a Motion Picture (movie), Golden Globe Award: Best Supporting Actress in a Motion Picture (movie), Golden Globe Nominees 2026 (movie), Golden Globe Winners (movie), Academy Award for Best Actor (movie), Academy Award for Best Actress (movie), Academy Award for Best Adapted Screenplay (movie), Academy Award for Best Animated Feature (movie), Academy Award for Best Cinematography (movie), Academy Award for Best Costume Design (movie), Academy Award for Best Director (movie), Academy Award for Best Documentary Feature Film (movie), Academy Award for Best Film Editing (movie), Academy Award for Best Foreign Language Film (movie), Academy Award for Best Makeup and Hairstyling (movie), Academy Award for Best Original Score (movie), Academy Award for Best Original Screenplay (movie), Academy Award for Best Original Song (movie), Academy Award for Best Picture (movie), Academy Award for Best Production Design (movie), Academy Award for Best Sound (movie), Academy Award for Best Supporting Actor (movie), Academy Award for Best Supporting Actress (movie), Academy Award for Best Visual Effects (movie), Academy Award Nominees (movie), Academy Award Nominees & Winners (movie), Academy Award Nominees (movie), Venice Film Festival - All Films (movie), 20s Movies (movie), 10s Movies (movie), 00s Movies (movie), 90s Movies (movie), 80s Movies (movie), 70s Movies (movie), Latest TV Shows (series)
- **anilist** (1): Trending Anime (`anilist.trending`, anime)
- **mal** (2): Top Anime (`mal.discover.anime.top_anime.mnxr57of`, anime), Top Anime Movies (`mal.discover.anime.top_anime_movies.mnxr68mk`, anime)
- **tmdb** (178): Netflix — New (movie), Netflix — New (series), Netflix — Popular (movie), Netflix — Popular (series), Netflix — Top Rated (movie), Netflix — Top Rated (series), Netflix — Originals (movie), Netflix — Originals (series), Disney+ — New (movie), Disney+ — New (series), Disney+ — Popular (movie), Disney+ — Popular (series), Disney+ — Top Rated (movie), Disney+ — Top Rated (series), Disney+ — Originals (series), Apple TV — New (movie), Apple TV — New (series), Apple TV — Popular (movie), Apple TV — Popular (series), Apple TV — Top Rated (movie), Apple TV — Top Rated (series), Apple TV — Originals (movie), Apple TV — Originals (series), Prime Video — New (movie), Prime Video — New (series), Prime Video — Popular (movie), Prime Video — Popular (series), Prime Video — Top Rated (movie), Prime Video — Top Rated (series), Prime Video — Originals (movie), Prime Video — Originals (series), HBO Max — New (movie), HBO Max — New (series), HBO Max — Popular (movie), HBO Max — Popular (series), HBO Max — Top Rated (movie), HBO Max — Top Rated (series), HBO Max — Originals (movie), HBO Max — Originals (series), Hulu — New (movie), Hulu — New (series), Hulu — Popular (movie), Hulu — Popular (series), Hulu — Top Rated (movie), Hulu — Top Rated (series), Hulu — Originals (series), Paramount+ — New (movie), Paramount+ — New (series), Paramount+ — Popular (movie), Paramount+ — Popular (series), Paramount+ — Top Rated (movie), Paramount+ — Top Rated (series), Paramount+ — Originals (series), Peacock — New (movie), Peacock — New (series), Peacock — Popular (movie), Peacock — Popular (series), Peacock — Top Rated (movie), Peacock — Top Rated (series), Peacock — Originals (series), Starz — New (movie), Starz — New (series), Starz — Popular (movie), Starz — Popular (series), Starz — Top Rated (movie), Starz — Top Rated (series), Starz — Originals (series), Shudder — New (movie), Shudder — New (series), Shudder — Popular (movie), Shudder — Popular (series), Shudder — Top Rated (movie), Shudder — Top Rated (series), Shudder — Originals (series), Adult Swim — New (movie), Adult Swim — New (series), Adult Swim — Popular (movie), Adult Swim — Popular (series), Adult Swim — Top Rated (movie), Adult Swim — Top Rated (series), Adult Swim — Originals (movie), Adult Swim — Originals (series), Action — New (movie), Action — New (series), Action — Popular (movie), Action — Popular (series), Action — Top Rated (movie), Action — Top Rated (series), Animation — New (movie), Animation — New (series), Animation — Popular (movie), Animation — Popular (series), Animation — Top Rated (movie), Animation — Top Rated (series), Comedy — New (movie), Comedy — New (series), Comedy — Popular (movie), Comedy — Popular (series), Comedy — Top Rated (movie), Comedy — Top Rated (series), Crime — New (movie), Crime — New (series), Crime — Popular (movie), Crime — Popular (series), Crime — Top Rated (movie), Crime — Top Rated (series), Documentary — New (movie), Documentary — New (series), Documentary — Popular (movie), Documentary — Popular (series), Documentary — Top Rated (movie), Documentary — Top Rated (series), Drama — New (movie), Drama — New (series), Drama — Popular (movie), Drama — Popular (series), Drama — Top Rated (movie), Drama — Top Rated (series), Family — New (movie), Family — New (series), Family — Popular (movie), Family — Popular (series), Family — Top Rated (movie), Family — Top Rated (series), History — New (movie), History — New (series), History — Popular (movie), History — Popular (series), History — Top Rated (movie), History — Top Rated (series), Horror — New (movie), Horror — New (series), Horror — Popular (movie), Horror — Popular (series), Horror — Top Rated (movie), Horror — Top Rated (series), Mystery — New (movie), Mystery — New (series), Mystery — Popular (movie), Mystery — Popular (series), Mystery — Top Rated (movie), Mystery — Top Rated (series), Romance — New (movie), Romance — New (series), Romance — Popular (movie), Romance — Popular (series), Romance — Top Rated (movie), Romance — Top Rated (series), Sci-Fi — New (movie), Sci-Fi — New (series), Sci-Fi — Popular (movie), Sci-Fi — Popular (series), Sci-Fi — Top Rated (movie), Sci-Fi — Top Rated (series), Thriller — New (movie), Thriller — Popular (movie), Thriller — Top Rated (movie), Reality TV — New (series), Reality TV — Popular (series), Reality TV — Top Rated (series), Nature — New (movie), Nature — New (series), Nature — Popular (movie), Nature — Popular (series), Nature — Top Rated (movie), Nature — Top Rated (series), Anime — New (movie), Anime — Popular (movie), Anime — Top Rated (movie), Anime — New (series), Anime — Popular (series), Anime — Top Rated (series), Trending Movies (movie), Trending Series (series), Popular Movies (movie), Popular Series (series), Top Rated Movies (movie), Top Rated Series (series)

### Friends profile — `aiometadata-no-collections`

46 catalogs, 27 enabled. Sources: tmdb 10, tvdb 5, tvmaze 1, mal 18, streaming 12.

- **tmdb** (10): Popular (`tmdb.top`, movie), Popular (`tmdb.top`, series), Trending (`tmdb.trending`, movie), Trending (`tmdb.trending`, series), Top Rated (`tmdb.top_rated`, movie), Top Rated (`tmdb.top_rated`, series), TMDB By Year (`tmdb.year`, movie), TMDB By Year (`tmdb.year`, series), TMDB By Language (`tmdb.language`, movie), TMDB By Language (`tmdb.language`, series)
- **tvdb** (5): TVDB Trending (`tvdb.trending`, movie), TVDB Trending (`tvdb.trending`, series), TVDB Genres (`tvdb.genres`, movie), TVDB Genres (`tvdb.genres`, series), TVDB Collections (`tvdb.collections`, movie)
- **tvmaze** (1): TVmaze Daily Schedule (`tvmaze.schedule`, series, off)
- **mal** (18): MAL Airing Now (`mal.airing`, anime, off), MAL Upcoming Season (`mal.upcoming`, anime, off), MAL Airing Schedule (`mal.schedule`, anime, off), MAL Seasons (`mal.seasons`, anime, off), MAL Best of 80s (`mal.80sDecade`, anime, off), MAL Best of 90s (`mal.90sDecade`, anime, off), MAL Best of 2000s (`mal.00sDecade`, anime, off), MAL Best of 2010s (`mal.10sDecade`, anime, off), MAL Best of 2020s (`mal.20sDecade`, anime, off), MAL Genres (`mal.genres`, anime, off), MAL By Studio (`mal.studios`, anime, off), MAL Top Movies (`mal.top_movies`, anime, off), MAL Top Series (`mal.top_series`, anime, off), MAL Most Favorites (`mal.most_favorites`, anime, off), MAL Most Popular (`mal.most_popular`, anime, off), MAL Top Anime (`mal.top_anime`, anime, off), MAL Top Rated This Week (`mal.season_top`, anime, off), MAL Top New This Week (`mal.season_top_new`, anime, off)
- **streaming** (12): Netflix (Movies) (`streaming.nfx`, movie), Netflix (Series) (`streaming.nfx`, series), HBO Max (Movies) (`streaming.hbm`, movie), HBO Max (Series) (`streaming.hbm`, series), Disney+ (Movies) (`streaming.dnp`, movie), Disney+ (Series) (`streaming.dnp`, series), Prime Video (Movies) (`streaming.amp`, movie), Prime Video (Series) (`streaming.amp`, series), Apple TV+ (Movies) (`streaming.atp`, movie), Apple TV+ (Series) (`streaming.atp`, series), Crave (Movies) (`streaming.crv`, movie), Crave (Series) (`streaming.crv`, series)

## Provenance

This repo was `nuvio-settings`, which also carried the generator that produced an importable
catalog setup from a curated overlay (`build.py`, `curation.json`, `base/`, `data/`, `dist/`,
`tools/`, `reference/`). That pipeline was removed to leave a template; it is intact in git
history at the commit before the cleanup — `git show <commit>^:build.py` and friends. Its last
state built AIOMetadata **1.35.2** artifacts while the live instance had moved to **3.2.3**.

