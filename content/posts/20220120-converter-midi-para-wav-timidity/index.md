---
title: "Como converter músicas .midi para arquivos .wav com TiMidity++"
date: 2022-01-20
author: Komesu, D. K.
slug: converter-midi-para-wav-timidity
aliases:
    - /converter-midi-para-wav-timidity
tags: ["MIDI", "WAV", "Áudio"]
---

É possível converter arquivos de música MIDI para o formato WAV com a ferramenta Timidity++, um software sintetizador que consegue tocar MIDI sem precisar de um sintetizador de hardware.

<!--more-->

- [Timidity++](https://sourceforge.net/projects/timidity/)

Para instalar via APT no Debian e derivados use o seguinte comando:

```sh
sudo apt install timidity
```

Comando para converter arquivos MIDI para WAV:

```sh
timidity arquivo.midi -Ow -o arquivo.wav
```

Links:

- [Resposta de Franck Dernoncourt no StackExchange SoftwareRecs](https://softwarerecs.stackexchange.com/a/10921)
- [Página do projeto TiMidity++ no SourceForge](http://sourceforge.net/projects/timidity/)
