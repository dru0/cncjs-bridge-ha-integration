# CNCjs Bridge HA Integration — v0.1.0

Osobna integracja Home Assistant, współpracująca z istniejącym `bridge.js`.
Nie zastępuje usługi Node.js ani sterowania LED WS2812.

## Wymagania
- Działający bridge, który zapisuje stan do `sensor.cncjs_status` przez REST API Home Assistant.
- Home Assistant z obsługą integracji niestandardowych.

## Instalacja ręczna
Skopiuj `custom_components/cncjs_bridge_companion` do katalogu `config/custom_components/` Home Assistant, uruchom ponownie HA i dodaj integrację `CNCjs Bridge Companion` w Ustawienia → Urządzenia i usługi → Dodaj integrację. Wybierz `sensor.cncjs_status`.

## Instalacja przez HACS
Po opublikowaniu folderu `custom_components` oraz `hacs.json` w głównym katalogu repozytorium dodaj adres repozytorium jako niestandardowe repozytorium kategorii Integracja. Zainstaluj integrację i uruchom ponownie HA.

## Encje
- Status — kopia stanu istniejącego `sensor.cncjs_status` z atrybutami.
- Połączenie CNCjs — z atrybutu `socket_connected`.
- Połączenie USB lasera — z atrybutu `serial_connected`.
- Zadanie aktywne — z atrybutu `job_active`.

Integracja działa lokalnie i reaguje na zmiany encji źródłowej; nie łączy się bezpośrednio z CNCjs. Oryginalna encja i automatyzacje pozostają bez zmian. Jeśli bridge przestanie aktualizować encję, ostatni stan może pozostać widoczny — ta wersja nie wykrywa utraty heartbeat na podstawie czasu.

**Bezpieczeństwo:** status programu nie jest niezależnym potwierdzeniem zatrzymania lasera. Nie używaj tych encji jako jedynego zabezpieczenia stanowiska.

## Repozytoria
- Integracja HACS: https://github.com/dru0/cncjs-bridge-ha-integration
- Bridge Raspberry Pi: https://github.com/dru0/cncjs-bridge-ha
