# 🤝 Guía de Contribución - ArduCheck

¡Gracias por tu interés en contribuir a **ArduCheck**! Este proyecto es de código abierto y está mantenido por **KherCent**. Tu ayuda es fundamental para mejorar el diagnóstico de hardware en todo el ecosistema de Arduino.

Al participar en este proyecto, te comprometes a seguir nuestro [Código de Conducta](CODE_OF_CONDUCT.md).

[English Version](CONTRIBUTING.md) | **Español**

---

## 🗂️ ¿Cómo puedo contribuir?

### 1. Reportar Errores (Bugs)
Si encuentras un error o un comportamiento inesperado:
1. Revisa la lista de [Issues del proyecto](https://github.com/KherCent/ArduCheck/issues) para asegurarte de que no haya sido reportado previamente.
2. Si es nuevo, abre un Issue usando nuestra plantilla de **Bug Report**.
3. Asegúrate de incluir:
   - Sistema operativo (Windows, Linux, macOS).
   - Placa de Arduino exacta y si es original o clon (ej. CH340).
   - Log completo del terminal o captura de la GUI.
   - Pasos detallados para reproducir el error.

### 2. Proponer Nuevas Funciones o Arquitecturas
Queremos diagnosticar tantas placas como sea posible. Si deseas proponer soporte para una nueva placa, chip o arquitectura:
1. Abre un Issue usando la plantilla **Feature Request**.
2. Explica qué placas se beneficiarían y, si es posible, proporciona los IDs de USB (`VID:PID`) y la firma del chip.

### 3. Contribuir con Código (Pull Requests)
¡Nos encantan las Pull Requests (PR)! Para contribuir con código, sigue este flujo de trabajo:

1. **Haz un Fork** del repositorio a tu propia cuenta.
2. **Clona** tu fork localmente:
   ```bash
   git clone https://github.com/TU-USUARIO/ArduCheck.git
   cd ArduCheck
   ```
3. **Crea una rama (branch)** descriptiva para tus cambios:
   ```bash
   git checkout -b feature/mi-nueva-funcion
   # o para correcciones
   git checkout -b fix/correccion-de-bug
   ```
4. **Realiza tus cambios** y asegúrate de seguir las pautas de estilo.
5. **Prueba tus cambios**:
   - Ejecuta los tests automáticos: `python -m unittest tests/test_smoke.py`
   - Si modificaste el firmware, asegúrate de que compila correctamente usando `arduino-cli`.
6. **Haz commit** de tus cambios de forma limpia y clara.
7. **Sube tus cambios** a tu fork y abre una **Pull Request** hacia la rama `main` del repositorio oficial.

---

## 🎨 Pautas de Estilo y Código

### Python (Host CLI & GUI)
- Seguimos la guía de estilo **PEP 8**.
- Usa comentarios en el código cuando la lógica sea compleja.
- Mantén la compatibilidad multiplataforma (evita llamadas directas al sistema operativo que no sean portables).

### Firmware C/C++ (Sketches en `firmware/`)
- El código del firmware debe ser lo más ligero y eficiente posible.
- Evita el uso de librerías externas que no puedan instalarse fácilmente desde el gestor oficial de librerías de Arduino.
- Estructura las pruebas de forma modular para que la salida por el puerto Serial sea consistente y fácil de parsear por `core/parser.py`.

---

¿Tienes alguna pregunta? No dudes en abrir un hilo de discusión o contactar al mantenedor del proyecto, **KherCent**. ¡Feliz código!
