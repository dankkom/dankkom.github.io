---
title: "Códigos de Formato de Data e Hora: strftime(), strptime()"
date: 2022-04-01
author: Komesu, D. K.
slug: codigos-strftime-strptime
tags: []
---

Todos os códigos de formato de data/hora do padrão C 1989.

<!--more-->

<table>
    <thead>
        <tr>
            <th>Directive</th>
            <th>Meaning</th>
            <th>Example</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><code>%a</code></td>
            <td>Weekday as locale’s abbreviated name.</td>
            <td>Sun, Mon, …, Sat (en_US);So, Mo, …, Sa (de_DE)</td>
        </tr>
        <tr>
            <td><code>%A</code></td>
            <td>Weekday as locale’s full name.</td>
            <td>Sunday, Monday, …, Saturday (en_US);Sonntag, Montag, …, Samstag (de_DE)</td>
        </tr>
        <tr>
            <td><code>%w</code></td>
            <td>Weekday as a decimal number, where 0 is Sunday and 6 is Saturday.</td>
            <td>0, 1, …, 6</td>
            </tr>
        <tr>
            <td><code>%d</code></td>
            <td>Day of the month as a zero-padded decimal number.</td>
            <td>01, 02, …, 31</td>
        </tr>
        <tr>
            <td><code>%b</code></td>
            <td>Month as locale’s abbreviated name.</td>
            <td>Jan, Feb, …, Dec (en_US);Jan, Feb, …, Dez (de_DE)</td>
        </tr>
        <tr>
            <td><code>%B</code></td>
            <td>Month as locale’s full name.</td>
            <td>January, February, …, December (en_US);Januar, Februar, …, Dezember (de_DE)</td>
        </tr>
        <tr>
            <td><code>%m</code></td>
            <td>Month as a zero-padded decimal number.</td>
            <td>01, 02, …, 12</td>
        </tr>
        <tr>
            <td><code>%y</code></td>
            <td>Year without century as a zero-padded decimal number.</td>
            <td>00, 01, …, 99</td>
        </tr>
        <tr>
            <td><code>%Y</code></td>
            <td>Year with century as a decimal number.</td>
            <td>0001, 0002, …, 2013, 2014, …, 9998, 9999</td>
        </tr>
        <tr>
            <td><code>%H</code></td>
            <td>Hour (24-hour clock) as a zero-padded decimal number.</td>
            <td>00, 01, …, 23</td>
        </tr>
        <tr>
            <td><code>%I</code></td>
            <td>Hour (12-hour clock) as a zero-padded decimal number.</td>
            <td>01, 02, …, 12</td>
        </tr>
        <tr>
            <td><code>%p</code></td>
            <td>Locale’s equivalent of either AM or PM.</td>
            <td>AM, PM (en_US);am, pm (de_DE)</td>
        </tr>
        <tr>
            <td><code>%M</code></td>
            <td>Minute as a zero-padded decimal number.</td>
            <td>00, 01, …, 59</td>
        </tr>
        <tr>
            <td><code>%S</code></td>
            <td>Second as a zero-padded decimal number.</td>
            <td>00, 01, …, 59</td>
        </tr>
        <tr>
            <td><code>%f</code></td>
            <td>Microsecond as a decimal number, zero-padded to 6 digits.</td>
            <td>000000, 000001, …, 999999</td>
        </tr>
        <tr>
            <td><code>%z</code></td>
            <td>UTC offset in the form&nbsp;<code>±HHMM[SS[.ffffff]]</code>&nbsp;(empty string if the object is naive).</td>
            <td>(empty), +0000, -0400, +1030, +063415, -030712.345216</td>
        </tr>
        <tr>
            <td><code>%Z</code></td>
            <td>Time zone name (empty string if the object is naive).</td>
            <td>(empty), UTC, GMT</td>
        </tr>
        <tr>
            <td><code>%j</code></td>
            <td>Day of the year as a zero-padded decimal number.</td>
            <td>001, 002, …, 366</td>
        </tr>
        <tr>
            <td><code>%U</code></td>
            <td>Week number of the year (Sunday as the first day of the week) as a zero-padded decimal number. All days in a new year preceding the first Sunday are considered to be in week 0.</td>
            <td>00, 01, …, 53</td>
        </tr>
        <tr>
            <td><code>%W</code></td>
            <td>Week number of the year (Monday as the first day of the week) as a zero-padded decimal number. All days in a new year preceding the first Monday are considered to be in week 0.</td>
            <td>00, 01, …, 53</td>
        </tr>
        <tr>
            <td><code>%c</code></td>
            <td>Locale’s appropriate date and time representation.</td>
            <td>Tue Aug 16 21:30:00 1988 (en_US);Di 16 Aug 21:30:00 1988 (de_DE)</td>
        </tr>
        <tr>
            <td><code>%x</code></td>
            <td>Locale’s appropriate date representation.</td>
            <td>08/16/88 (None);08/16/1988 (en_US);16.08.1988 (de_DE)</td>
        </tr>
        <tr>
            <td><code>%X</code></td>
            <td>Locale’s appropriate time representation.</td>
            <td>21:30:00 (en_US);21:30:00 (de_DE)</td>
        </tr>
        <tr>
            <td><code>%%</code></td>
            <td>A literal&nbsp;<code>'%'</code>&nbsp;character.</td>
            <td>%</td>
        </tr>
    </tbody>
</table>

Diretivas adicionais não requeridas pelo padrão C89.

<table>
    <thead>
        <tr>
            <th>Directive</th>
            <th>Meaning</th>
            <th>Example</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><code>%G</code></td>
            <td>ISO 8601 year with century representing the year that contains the greater part of the ISO week (<code>%V</code>).</td>
            <td>0001, 0002, …, 2013, 2014, …, 9998, 9999</td>
        </tr>
        <tr>
            <td><code>%u</code></td>
            <td>ISO 8601 weekday as a decimal number where 1 is Monday.</td>
            <td>1, 2, …, 7</td>
        </tr>
        <tr>
            <td><code>%V</code></td>
            <td>ISO 8601 week as a decimal number with Monday as the first day of the week. Week 01 is the week containing Jan 4.</td>
            <td>01, 02, …, 53</td>
        </tr>
    </tbody>
</table>

---

## Referências

[Python Documentation - datetime library: strftime and strptime format codes](//docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)
