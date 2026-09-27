## Objetivo del trabajo

El objetivo de este trabajo es diseñar e implementar un sistema de agarre ajustable y automatizado que permita la conexión humano-robot en el contexto de la rehabilitación física. El agarre debe adaptarse a diferentes partes del brazo del paciente (bíceps, antebrazo, muñeca...) para facilitar los procesos de terapia asistida mediante los robots KUKA, especialmente en pacientes con movilidad reducida que no puedan sujetarse al robot por sí mismos.

## Consideraciones a tener en cuenta

- Fácil de intercambiar entre pacientes, para no ralentizar los procesos de rehabilitación.
- Fácil de usar, tanto para el paciente como para el fisioterapeuta.
- Interior acolchado, para mayor comodidad y seguridad del paciente.
- Ajuste automático a la circunferencia del brazo del paciente.
- Mecanismo de *quick release* independiente del cierre automático, para poder liberar al paciente de forma rápida y segura ante cualquier imprevisto.
- Diseño 3D parametrizado (a desarrollar en OnShape), que permita adaptar fácilmente las dimensiones del agarre a distintos tamaños de brazo.
- Valorar si conviene incluir también un agarre para la mano, posiblemente de tipo retráctil.

## Ideas a desarrollar

A partir de una primera sesión de brainstorming, se plantean las siguientes líneas de diseño para el mecanismo de ajuste:

- **Sistema mecánico tipo BOA**: ajuste mediante una ruleta/dial que tensa cables, similar a los sistemas de cierre BOA usados en calzado y otros equipos deportivos.
- **Mano con carraca**: cierre progresivo tipo carraca (ratchet), que permite ajustar el agarre en pasos discretos y liberarlo rápidamente.
- **Agarre tipo tentáculo**: mecanismo flexible que se adapta a la forma del brazo por contacto.
- **Mano ajustable "underactuated"**: sistema con menos actuadores que grados de libertad, que se adapta pasivamente a la forma del brazo (concepto habitual en manos robóticas antropomórficas).
- **Sistema neumático**: brazalete inflable que se ajusta mediante presión de aire, repartiendo la fuerza de forma uniforme sobre el brazo.

## Idea 1: Sistema mecánico tipo BOA

### Descripción

Sistema de ajuste basado en un dial/ruleta que tensa uno o varios cables mediante un carrete interno. Es la tecnología usada en calzado deportivo, rodilleras, tobilleras, muñequeras y encajes protésicos comerciales.

<img width="320" height="566" alt="image" src="https://github.com/user-attachments/assets/cb432f8d-d301-4ce4-9d7d-84b8f987d761" />


### Opinión / valoración

Puntos a favor respecto a nuestros objetivos:

- Reparte la presión de forma uniforme sobre el brazo, evitando puntos de presión concentrados (relevante en pacientes con sensibilidad reducida por ictus).
- Permite ajuste en incrementos sub-milimétricos, con precisión suficiente para adaptarse a distintos diámetros de bíceps/antebrazo.
- Existen versiones motorizadas ya validadas en dispositivos médicos reales, por lo que no es una tecnología experimental.

Puntos en contra:

- El mecanismo de cable + carrete no es trivial de fabricar/mantener. (los módulos BOA son cerrados y patentados, difícil de replicar barato en OnShape + impresión 3D).
- La apertura total es más lenta que un pestillo mecánico simple, por lo que el *quick release* debería ser un mecanismo independiente del carrete, no depender de él.

### Propuesta de control

Arquitectura basada en cómo lo resuelven los sistemas motorizados existentes (ver patente de BOA):

1. **Actuador**: motor DC pequeño + reductora de varias etapas, para conseguir suficiente par a baja velocidad.
2. **Mecanismo de tres modos**:
   - *Apriete*: el engranaje motor embraga contra el carrete (tipo trinquete) y lo hace girar, enrollando el cable.
   - *Aflojado incremental*: el motor invierte y libera el carrete en ciclos cortos de engranar/desengranar, soltando tensión de forma controlada.
   - *Liberación total*: el carrete queda libre para girar sin oposición del motor (posible base para el mecanismo de *quick release*).
3. **Control de fuerza vía corriente del motor**: monitorizando la corriente a través de un puente en H, ya que una corriente determinada corresponde a una tensión de cable conocida. Es barato, pero no refleja la presión real sobre el tejido — conviene complementarlo con un sensor de presión o galga extensométrica en el cable/brazalete.
4. **Resorte auxiliar**: un muelle independiente que recoge holgura del cable cuando el motor está apagado, manteniendo contacto mínimo sin gasto energético continuo.

Para la integración con el FlexPendant: el lazo de control de corriente/tensión viviría en un microcontrolador local (driver de motor con lazo de corriente), exponiendo hacia el controlador KUKA solo comandos de alto nivel (apretar / aflojar / liberar + estado de tensión actual).

### Referencias

- [US9248040B2 — Motorized tensioning system for medical braces and devices (Boa Technology)](https://patents.google.com/patent/US9248040B2/en) — patente con el mecanismo de motor/embrague/control por corriente descrito arriba.
- [The exoskeleton prototype including the Boa Closure System (ResearchGate)](https://www.researchgate.net/figure/The-exoskeleton-prototype-including-the-Boa-Closure-System_fig3_324040549) — ejemplo de sistema BOA aplicado directamente sobre un exoesqueleto.

<img width="822" height="745" alt="image" src="https://github.com/user-attachments/assets/acf87d65-0747-4886-acf1-e2930d31d5ff" />

