# 🔒 Política de Seguridad - Arduino Diagnostic Suite

## Versiones Soportadas

| Version | Estado | Soporte hasta |
|---------|--------|---------------|
| 1.x.x   | ⚠️ Beta | En desarrollo |

## Reportar una Vulnerabilidad

Si descubres una vulnerabilidad de seguridad en Arduino Diagnostic Suite, por favor repórtala de forma responsable:

### Canal preferido
1. **NO abras un Issue público** en GitHub para vulnerabilidades de seguridad.
2. Envía un correo electrónico privado a **KherCent** con:
   - Descripción detallada de la vulnerabilidad.
   - Pasos para reproducirla.
   - Posibles impactos y severidad.
   - Sugerencias de corrección (si las tienes).

### Qué esperar
- Reconocimiento de recepción dentro de **48 horas**.
- Actualización sobre el progreso dentro de **7 días**.
- Crédito en el changelog de seguridad (si lo deseas).

### Scope de seguridad
Las siguientes áreas están dentro del scope de revisión:
- Acceso no autorizado a puertos seriales.
- Ejecución de código arbitrario a través de payloads en Serial.
- Acceso a archivos del sistema a través de paths traversal.
- Inyección de comandos en llamadas a `arduino-cli` / `avrdude`.

### Fuera del scope
- Ataques de denegación de servicio locales (requiere acceso físico a la maquina).
- Vulnerabilidades en herramientas de terceros (`arduino-cli`, `avrdude`).
- Configuraciones de sistema operativo inseguras.

## Historial de Seguridad

| Fecha | Severidad | Descripcion | Estado |
|-------|-----------|-------------|--------|
| - | - | Ninguna vulnerabilidad reportada | - |

---

**KherCent** se compromete a mantener este proyecto seguro. Gracias por tu ayuda.
