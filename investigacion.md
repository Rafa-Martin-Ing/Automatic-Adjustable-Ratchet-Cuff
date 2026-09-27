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

## Idea 2a: Brazalete neumático inflable

### Descripción

Brazalete de cámara única que envuelve todo el brazo y se infla de forma uniforme, similar al manguito de un tensiómetro digital.

<img width="1167" height="593" alt="image" src="https://github.com/user-attachments/assets/cee0612a-13a9-4647-9123-4b4f553ec9b8" />


### Ventajas

- Reparte la presión de forma uniforme sobre toda la circunferencia del brazo.
- Mecánicamente simple: una sola cámara, geometría sencilla de fabricar.
- Ajuste continuo de presión, sin partes móviles rígidas expuestas al paciente.
- *Quick release* trivial de implementar: una válvula de purga rápida abre la cámara a la atmósfera y la presión cae casi al instante.

### Desventajas

- El robot no tiene actualmente sistema neumático instalado, por lo que habría que añadir generación de aire propia (micro-compresor local + batería, o cartuchos de CO2 desechables que habría que recargar/cambiar entre pacientes).
- No se adapta bien a formas no cilíndricas: el brazo no es un cilindro perfecto y cambia de forma con la contracción muscular, por lo que la presión no queda tan uniforme como en teoría.
- Tiempo de inflado/desinflado más lento que un mecanismo mecánico (carraca, BOA).
- Riesgo de fugas de aire a largo plazo → mantenimiento periódico.

### Propuesta de aplicación / control

Compresor local en miniatura (o línea compartida entre los dos KUKA) + válvula proporcional, con sensor de presión interno en la cámara. El lazo de control infla hasta alcanzar una **presión de contacto objetivo** (no una presión de cámara fija), para adaptarse a brazos de distinto grosor. El *quick release* se resuelve con una electroválvula de purga rápida, mecánicamente independiente del circuito de inflado.

---

## Idea 2b: Dedos/pinzas neumáticas con endoesqueleto rígido

### Descripción

En vez de un brazalete continuo, 2–3 "dedos" blandos neumáticos dispuestos radialmente alrededor del brazo. Cada dedo tiene un endoesqueleto rígido interno (da forma y evita que colapse) recubierto de una piel de silicona inflable. Al inflarse, cada dedo se curva de forma independiente y envuelve el contorno del brazo — concepto tomado de un gripper robótico de manipulación (imagen de referencia: dedos que cierran un hueco alrededor de un objeto).

<img width="524" height="595" alt="image" src="https://github.com/user-attachments/assets/2ef3bc41-84d9-428f-9c59-efa779b0bccc" />
<img width="644" height="309" alt="image" src="https://github.com/user-attachments/assets/aac38115-d97a-4fad-834a-fa973545c8a8" />

### Ventajas

- Se adapta a formas no cilíndricas, ya que cada dedo se pliega de forma independiente según lo que encuentra (a diferencia de la presión radial uniforme del brazalete).
- El endoesqueleto rígido facilita integrar el sensor de presión de contacto directamente en cada dedo.
- Posible "palma activa" (como en el paper de referencia) para reconfigurar la postura de los dedos y adaptarse mejor a distintas partes del brazo (bíceps vs. antebrazo).

### Desventajas

- Mecánicamente más complejo de fabricar (moldeo de piel de silicona + endoesqueleto rígido), más difícil de replicar en el laboratorio sin experiencia previa en *soft robotics*.
- Requiere varias cámaras de aire independientes con sus propias válvulas → más componentes neumáticos que el brazalete simple.
- También depende de un sistema neumático que el robot no tiene actualmente instalado.
- Menos maduro/probado en aplicaciones médicas reales que un brazalete tipo tensiómetro; el paper de referencia es de manipulación robótica, no de uso clínico directo.

### Propuesta de aplicación / control

Cada dedo con su propia línea de aire y válvula proporcional (o electroválvula on/off con PWM), realimentado por un sensor de presión interno por cámara, controlando hasta una presión de contacto objetivo por dedo. El *quick release* se resolvería con una electroválvula de purga rápida que abre las tres cámaras a la atmósfera simultáneamente.

---

### Referencias

- [A portable inflatable soft wearable robot to assist the shoulder during industrial work (Science Robotics)](https://www.science.org/doi/10.1126/scirobotics.adi2377) — ejemplo de sistema neumático portátil, sin compresor de planta fijo, relevante para el problema de que el robot no tenga neumática instalada.
- [Decoupled, wearable soft robotic rehabilitation device for the upper limb (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12441639/) — dispositivo blando neumático wearable aplicado a rehabilitación de miembro superior.
- [A Soft Robotic Gripper With an Active Palm and Reconfigurable Fingers for Fully Dexterous In-Hand Manipulation (HAL / IEEE RAL, Pagoli et al.)](https://uca.hal.science/hal-03583792v1/document) — paper del que sale el concepto de dedos blandos con endoesqueleto rígido, piel inflable y palma activa.

