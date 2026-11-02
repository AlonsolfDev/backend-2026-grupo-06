# Informe de Calidad y Pruebas — API Backend

**Asignatura:** Desarrollo de Backend (ICINF1108)  
**Nombre:** Tomás  
**Fecha de ejecución de las evidencias:** 2 de noviembre de 2026 (según capturas)  
**Herramientas observadas:** FastAPI, Swagger UI, Uvicorn, SQLAlchemy y SQLite (confirmado por traceback).  
**Estado del informe:** resultados reales documentados; se identifican pendientes sin atribuirles pruebas exitosas.

> **Cómo abrir este informe:** conservar este archivo y la carpeta `evidencias/` en la misma ubicación relativa. GitHub mostrará las imágenes automáticamente. No mover las imágenes fuera de la carpeta sin actualizar los enlaces.

## 1. Alcance y criterio de aceptación

El trabajo de Calidad y Pruebas verifica endpoints, casos exitosos y de error, consulta con filtro/orden/paginación, persistencia tras reiniciar y evidencias reproducibles. La guía del proyecto exige al menos seis casos con **entrada, esperado y obtenido**, y evidencias; también exige levantar el proyecto desde una copia limpia siguiendo el README, y respuestas de error JSON uniformes.

**Criterio del informe:** se distingue entre respuesta HTTP correcta, regla de negocio comprobada, defecto confirmado y hallazgo pendiente de validar. El código esperado `400` no se sustituye por `422` sin aclaración.

![Plan de trabajo asignado al área de Calidad y Pruebas](evidencias/00_plan_trabajo.png)

*Figura: Plan de trabajo asignado al área de Calidad y Pruebas.*
## 2. Resumen ejecutivo

- **Funcionalidades observadas como correctas:** listado de usuarios (200), creación de usuario (201), consulta de usuario inexistente (404), validación de nombre/correo (422), modificación de equipamiento (200), listado de salas (200), paginación y orden descendente (200), consulta combinada de salas (200), persistencia de estado de equipamiento al reiniciar Uvicorn, confirmación repetida de reserva (200) y validación de fechas incoherentes (422).
- **Defecto observado D-01:** un correo duplicado devuelve 500, mientras la base de datos rechaza la duplicación por `UNIQUE`; para un conflicto de duplicado debería existir una respuesta controlada 409 según el contrato esperado.
- **Hallazgo D-02 pendiente de validar con reglas acordadas:** una reserva para 50 personas en la sala de capacidad 30 fue creada (201) según la ejecución reportada por el responsable; **no existe captura adjunta de esa respuesta** y falta confirmar que la restricción sea un requisito de negocio del sistema.
- **Documentación pendiente:** la respuesta 404 apareció como `Undocumented` en Swagger. La validación de usuario 422 mostró un cuerpo distinto al formato uniforme requerido, mientras la validación de fechas 422 sí mostró `error/code/message/details`.
- **Cobertura adicional:** se comprobó que el solapamiento de reservas confirmadas devuelve 409 con error uniforme (CP-11); sigue pendiente obtener respuesta 400 para una regla de negocio implementada, demostrar que un filtro excluye registros de otro estado, probar copia limpia a partir de README y documentar mecanismo reproducible/restablecimiento de datos. No se ha verificado un reinicio del motor de BD.

## 3. Matriz de casos de prueba

| ID | Operación / entrada | Resultado esperado | Resultado obtenido | Evaluación | Evidencia |
|---|---|---|---|---|---|
| CP-01 | GET listado de usuarios, sin parámetros visibles | 200 y arreglo JSON | 200; dos usuarios con id, nombre, correo, rol y activo | Aprobado | 01 |
| CP-02 | POST `/usuarios`, Carlos Ramirez, correo único, rol estudiante | 201 y registro creado | 201; usuario creado con id 3 | Aprobado | 02–03 |
| CP-03 | GET `/usuarios/9999` | 404 y JSON de error | 404, `RESOURCE_NOT_FOUND`, estructura uniforme; Swagger indica `Undocumented` | Aprobado con observación | 04 |
| CP-04 | POST `/usuarios`, nombre `A`, correo `correo-invalido` | 422, rechazo del esquema | 422; errores de longitud mínima 2 y email inválido; estructura JSON distinta del formato exigido | Validaciones aprobadas; formato observado | 05 |
| CP-05 | POST `/usuarios` con correo del usuario CP-02 | 409 Conflict y mensaje uniforme | 500 Internal Server Error | **Fallido (D-01)** | 06, log |
| CP-06 | PATCH `/equipamientos/1/estado?nuevo_estado=danado`* | 200; estado cambia | 200; Proyector id 1 queda `danado`* | Aprobado | 08–10 |
| CP-06B | Repetir PATCH con el mismo estado | Comportamiento por contrato no definido | 200; se conserva el estado | Observación, **no valida 400** | 11 |
| CP-07A | GET `/salas?ordenar_por=id&direccion=asc&pagina=1&limite=1` | 200; id 1, total 2, total_paginas 2 | Coincide | Aprobado | 14 |
| CP-07B | GET `/salas?ordenar_por=id&direccion=desc&pagina=1&limite=1` | 200; id 2 | Coincide | Aprobado | 15 |
| CP-07C | GET `/salas?estado=disponible&ordenar_por=id&direccion=desc&pagina=1&limite=1` | 200; id 2, total 2 | Coincide; filtro no discrimina porque ambas salas están disponibles | Parcial: faltaría test de exclusión | 16–17 |
| CP-08 | GET `/equipamientos/1` antes y después de reiniciar servidor | 200 y estado persistente | 200; mismo estado en ambas consultas | Aprobado (reinicio API) | 18–19 |
| CP-09A | PATCH `/reservas/1/confirmar` para reserva ya confirmada | Sin regla de rechazo confirmada | 200; reserva sigue confirmada | Observación; no prueba 400 | 21–22 |
| CP-09B | POST `/reservas`, fin 14:00, inicio 15:00 | Rechazo de fechas incoherentes (400/422 según capa) | 422; `VALIDATION_ERROR`, `fecha_fin debe ser posterior a fecha_inicio` | Aprobado como validación (422), no como 400 | 23–24 |
| CP-10 | POST `/reservas`, 50 asistentes en sala id 1, capacidad 30 | Rechazo si regla de capacidad exigida | 201, informado por quien ejecutó la prueba | Hallazgo pendiente de corroborar con captura y requisitos | **Captura no proporcionada** |
| CP-11 | POST `/reservas`, sala 1, 02/11/2026 09:30–10:30, superpuesto con reserva confirmada 09:00–11:00 | Rechazo de conflicto de horario; 409 conforme al contrato de conflicto | **409 Conflict**, `error.code=CONFLICT`, mensaje de sala ocupada y `details=[]`; Swagger mostró Undocumented | Aprobado; documentar 409 en OpenAPI | 26 |
| CP-12 | POST `/reservas`, inicio y término 25/11/2026 10:00 | Rechazo por fechas iguales | **422**, comunicado por el usuario; sin captura | Validación rechaza; no acredita 400 | Sin captura |

\*Nota: en las capturas el estado aparece literalmente como `danado` (sin tilde), mientras en la explicación se denomina «dañado». Para reproducir se debe escoger el valor exacto ofrecido por Swagger, no asumir la escritura de la URL.

## 4. Ejecución detallada y capturas

### CP-01 — Consulta de usuarios (200)

**Entrada:** operación GET de listado de usuarios. **Esperado:** lista JSON y código 200. **Obtenido:** 200; dos usuarios en el listado inicial. **Estado:** aprobado. La captura no incluye la barra con la ruta completa; el recurso se identifica por los campos devueltos y el contexto de la prueba.

![GET de usuarios: código 200 y dos registros](evidencias/01_listado_usuarios_200.png)

*Figura: GET de usuarios: código 200 y dos registros.*
### CP-02 — Creación de usuario válido (201)

**Entrada:** `POST /usuarios` con los datos:

```json
{
  "nombre": "Carlos Ramirez",
  "correo": "carlos.ramirez.prueba2026@example.com",
  "rol": "estudiante"
}
```

**Esperado:** 201 Created. **Obtenido:** 201, id 3, `activo: true`. **Estado:** aprobado. La creación se ejecuta **una sola vez** para no crear registros de prueba innecesarios.

![Formulario JSON de POST /usuarios antes de ingresar el caso](evidencias/02_post_usuario_entrada.png)

*Figura: Formulario JSON de POST /usuarios antes de ingresar el caso.*

![POST /usuarios: 201 Created, usuario id 3](evidencias/03_post_usuario_201.png)

*Figura: POST /usuarios: 201 Created, usuario id 3.*
### CP-03 — Recurso inexistente (404)

**Entrada:** `GET /usuarios/9999`. **Esperado:** 404, recurso inexistente. **Obtenido:** 404 con `error.code=RESOURCE_NOT_FOUND`, `message=No existe un usuario con ID 9999.` y `details=[]`. **Estado:** aprobado con observación de OpenAPI: Swagger señala `Undocumented`.

![GET /usuarios/9999: 404 y JSON uniforme](evidencias/04_usuario_inexistente_404.png)

*Figura: GET /usuarios/9999: 404 y JSON uniforme.*
### CP-04 — Entrada inválida (422)

**Entrada:** `POST /usuarios` con nombre `A`, correo `correo-invalido` y rol `estudiante`. **Esperado:** rechazo 422. **Obtenido:** 422; validación de longitud mínima de 2 caracteres y formato de correo. **Estado:** código y reglas correctos; revisar consistencia del esquema JSON de error para este endpoint.

![POST /usuarios: error 422 con detalles de longitud y correo](evidencias/05_validacion_usuario_422.png)

*Figura: POST /usuarios: error 422 con detalles de longitud y correo.*
### CP-05 — Correo duplicado (defecto D-01)

**Entrada:** repetir POST del caso CP-02. **Esperado:** 409 Conflict y error controlado. **Obtenido:** 500 Internal Server Error, texto plano `Internal Server Error`. **Estado:** fallido.

**Diagnóstico sustentado en el log adjunto:** `sqlite3.IntegrityError: UNIQUE constraint failed: usuarios.correo` y `sqlalchemy.exc.IntegrityError` al ejecutar `self.db.commit()` en `usuario_repository.py`. La base de datos impide el duplicado pero la excepción no se traduce a HTTP 409. No se aplicó una corrección comprobada en este informe.

![POST /usuarios repetido: 500 Internal Server Error](evidencias/06_usuario_duplicado_500.png)

*Figura: POST /usuarios repetido: 500 Internal Server Error.*
### CP-06 — Actualización de equipamiento (200) y repetición

El listado inicial confirmó dos equipamientos: Proyector id 1, sala 1, y Pizarra digital id 2, sala 2; ambos inicialmente `disponible`. El `PATCH /equipamientos/1/estado` permitió seleccionar `disponible` o `danado` y devolvió 200 al pasar a `danado`. Repetir el estado devolvió también 200; no se ha acreditado que repetirlo esté prohibido.

![Endpoints de equipamientos en Swagger](evidencias/07_rutas_equipamientos.png)

*Figura: Endpoints de equipamientos en Swagger.*

![GET /equipamientos: dos equipamientos disponibles](evidencias/08_listado_equipamientos_200.png)

*Figura: GET /equipamientos: dos equipamientos disponibles.*

![Parámetros del PATCH de estado](evidencias/09_patch_estado_parametros.png)

*Figura: Parámetros del PATCH de estado.*

![PATCH del equipamiento id 1: nuevo estado y código 200](evidencias/10_patch_danado_200.png)

*Figura: PATCH del equipamiento id 1: nuevo estado y código 200.*

![PATCH repetido: código 200 y estado sin cambio](evidencias/11_patch_repetido_200.png)

*Figura: PATCH repetido: código 200 y estado sin cambio.*

### CP-07 — Consulta de salas: filtro, orden y paginación

**Datos base:** sala A101 id 1, capacidad 30; sala B202 id 2, capacidad 12; ambas `disponible`. El endpoint devuelve `items`, `total`, `pagina`, `limite` y `total_paginas`. Probado el orden ascendente y descendente y límite 1. La consulta combinada `estado=disponible&ordenar_por=id&direccion=desc&pagina=1&limite=1` devuelve id 2, total 2 y total_paginas 2.

**Limitación:** como ambas salas están disponibles, el resultado no demuestra que el filtro descarte una sala con otro estado; se requiere un conjunto de prueba mixto o un estado con cero coincidencias, verificando siempre el contrato.

![CRUD de salas disponible en Swagger](evidencias/12_rutas_salas.png)

*Figura: CRUD de salas disponible en Swagger.*

![GET /salas: dos salas, metadatos de paginación](evidencias/13_listado_salas_200.png)

*Figura: GET /salas: dos salas, metadatos de paginación.*

![Orden ascendente y límite 1: devuelve id 1](evidencias/14_paginacion_asc_200.png)

*Figura: Orden ascendente y límite 1: devuelve id 1.*

![Orden descendente y límite 1: devuelve id 2](evidencias/15_orden_desc_200.png)

*Figura: Orden descendente y límite 1: devuelve id 2.*

![Parámetros disponibles: estado, ordenar_por, direccion, pagina y limite](evidencias/16_parametros_filtro.png)

*Figura: Parámetros disponibles: estado, ordenar_por, direccion, pagina y limite.*

![Consulta combinada: estado disponible, orden desc, página 1, límite 1](evidencias/17_filtro_orden_paginacion_200.png)

*Figura: Consulta combinada: estado disponible, orden desc, página 1, límite 1.*

### CP-08 — Persistencia después de reiniciar Uvicorn

Se consultó `GET /equipamientos/1` antes de apagar la aplicación; el Proyector estaba `danado`. Se reinició Uvicorn y se repitió la misma consulta con respuesta 200 y el mismo estado. **Resultado:** aprobado como persistencia tras reinicio de la API. No se certificó reinicio separado del motor de base de datos.

![Estado del Proyector antes del reinicio: danado](evidencias/18_persistencia_antes.png)

*Figura: Estado del Proyector antes del reinicio: danado.*

![Estado del Proyector después del reinicio: danado](evidencias/19_persistencia_despues.png)

*Figura: Estado del Proyector después del reinicio: danado.*
### CP-09 — Reservas: confirmación repetida y fechas incoherentes

El listado de reservas mostró la reserva id 1 (`confirmada`) y la id 2 (`pendiente`), además de una tercera reserva parcialmente visible. `PATCH /reservas/1/confirmar` respondió 200 y mantuvo `confirmada`; sin una prohibición documentada, no constituye error de negocio.

En `POST /reservas` se enviaron `usuario_id=1`, `sala_id=1`, `fecha_inicio=2026-11-15T15:00:00`, `fecha_fin=2026-11-15T14:00:00`, `proposito=Prueba de calidad - fechas incorrectas`, `num_asistentes=5`. Se obtuvo **422** y error uniforme con mensaje de regla cronológica. Esta es una validación correcta; **no** prueba que se devuelva 400.

![Endpoints disponibles para reservas](evidencias/20_rutas_reservas.png)

*Figura: Endpoints disponibles para reservas.*

![GET /reservas: registros y estados](evidencias/21_listado_reservas_200.png)

*Figura: GET /reservas: registros y estados.*

![Confirmación repetida de reserva id 1: HTTP 200](evidencias/22_confirmacion_repetida_200.png)

*Figura: Confirmación repetida de reserva id 1: HTTP 200.*

![Campos exigidos en POST /reservas](evidencias/23_formulario_post_reserva.png)

*Figura: Campos exigidos en POST /reservas.*

![POST /reservas: fecha final anterior a inicial, error uniforme HTTP 422](evidencias/24_fechas_incoherentes_422.png)

*Figura: POST /reservas: fecha final anterior a inicial, error uniforme HTTP 422.*

### CP-10 — Reserva por encima de la capacidad: hallazgo pendiente

**Entrada reportada:** `POST /reservas` con `usuario_id=1`, `sala_id=1`, inicio `2026-11-20T10:00:00`, fin `2026-11-20T12:00:00`, propósito `Prueba de calidad - exceso de capacidad`, `num_asistentes=50`. La sala id 1 registraba capacidad 30. **Resultado comunicado:** HTTP 201 Created.



### CP-11 — Solapamiento con reserva confirmada (409)

**Entrada:** `POST /reservas` con `usuario_id=2`, `sala_id=1`, `fecha_inicio=2026-11-02T09:30:00`, `fecha_fin=2026-11-02T10:30:00`, `proposito=Prueba de calidad - conflicto de horario` y `num_asistentes=5`. Se superpone con la reserva confirmada del 02/11/2026 09:00–11:00.

**Resultado esperado:** rechazo del conflicto; HTTP 409 es apropiado para una reserva existente incompatible. **Resultado obtenido:** `409 Conflict` y JSON con `error.code=CONFLICT`, `message=La sala ya tiene una reserva confirmada en ese horario.` y `details=[]`. **Estado:** aprobado. La respuesta figura como `Undocumented` en Swagger; falta añadir la respuesta 409 al contrato OpenAPI.

![POST /reservas: rechazo de horario ocupado, HTTP 409](evidencias/26_conflicto_horario_reserva_409.png)

*Figura: CP-11 — Error 409 por conflicto de horario de reserva.*

### CP-12 — Fechas de inicio y término iguales (422, sin captura)

**Entrada comunicada:** `POST /reservas` con inicio y término `2026-11-25T10:00:00`, `usuario_id=1`, `sala_id=1`, `proposito=Prueba de calidad - fechas iguales`, `num_asistentes=5`. **Esperado:** rechazo. **Obtenido según el ejecutor:** HTTP 422. No se adjuntó evidencia gráfica. Este resultado tampoco acredita un HTTP 400.

### Revisión del código de negocio compartido

Se inspeccionaron fragmentos de `reserva_service.py` y `reglas_negocio.py` aportados por el equipo. `validar_fechas_reserva` lanza `ReglaNegocioError` cuando fin es menor o igual a inicio, pero en Swagger la validación se rechaza antes con 422, presumiblemente en el DTO. `validar_disponibilidad_sala` lanza `ConflictoError` al solaparse con una reserva confirmada, coherente con CP-11. `validar_equipamiento_disponible` lanza `ReglaNegocioError` si el equipamiento está dañado, pero no aparece invocada desde el fragmento compartido de `reserva_service.py`; además, el POST de reserva no presenta campo de equipamiento. No puede asumirse que esta regla esté expuesta y sea ejecutable por un endpoint.

En el fragmento examinado de `crear_reserva` tampoco se observó una comprobación de capacidad contra `num_asistentes`. Conviene confirmar si existe en otra capa o si la regla está declarada en los requisitos acordados. La revisión de fragmentos no sustituye una auditoría del repositorio completo.

## 5. Registro de incidencias y observaciones

| ID | Severidad sugerida | Hecho constatado | Acción recomendada | Estado |
|---|---|---|---|---|
| D-01 | Alta | POST usuario duplicado genera 500; el log muestra UNIQUE de `usuarios.correo` | Manejar error de integridad con rollback, respuesta 409 uniforme, documentarlo en OpenAPI y repetir CP-05 | Abierto |
| O-01 | Media | Swagger marca 404 de usuario como `Undocumented` | Declarar respuesta 404 en el endpoint OpenAPI | Pendiente |
| O-02 | Media | Respuesta 422 de usuario con estructura distinta al JSON `error/code/message/details`; la respuesta 422 de reserva sí es uniforme | Revisar manejador global de errores de validación y uniformidad | Pendiente |
| O-03 | Media | Solo se han observado salas en estado disponible | Crear datos aislados o escenario que pruebe exclusión por filtro | Pendiente |
| D-02 | Por confirmar | Reserva 50 asistentes en sala de capacidad 30 devolvió 201 (según reporte verbal) | Confirmar regla de dominio, adjuntar screenshot e ID, corregir si aplica y limpiar dato de prueba | Pendiente de corroborar |
| O-04 | Media | El log de esta ejecución muestra SQLite | Confirmar con el equipo si SQLite es la BD esperada para el entregable y README | Pendiente |
| O-05 | Media | No se ha obtenido un caso con 400 de negocio; fechas iguales también produjeron 422 | Revisar DTO y controlador de `ReglaNegocioError`; encontrar ruta que active 400 o justificar su ausencia según contrato | Pendiente |
| O-06 | Baja | El conflicto de reserva dio 409 correcto, pero Swagger lo indica como `Undocumented` | Documentar respuesta 409 en OpenAPI | Pendiente |

## 6. Reproducibilidad y limpieza de datos

1. Usar un entorno de **pruebas**, nunca la BD de producción o de otro integrante. Conservar los registros base de la demo o restaurarlos desde seeders/snapshot. No borrar registros id 1 o 2 sin coordinar.
2. Anotar base URL local real (observada `http://127.0.0.1:8000`), versión/commit probado, fecha y configuración sin secretos.
3. Ejecutar CP-01, CP-03 y CP-04 sin mutaciones. Para CP-02, emplear un correo único y guardar el ID asignado; reutilizarlo deliberadamente para CP-05.
4. Para CP-06, registrar estado original del equipamiento y restaurarlo después de la prueba si el grupo lo requiere. CP-08 depende del cambio previo: no restaurarlo antes de capturar el resultado posterior al reinicio.
5. Para CP-07, generar un juego de datos controlado de al menos dos estados de sala para demostrar que el filtro excluye registros, y restaurarlo al terminar.

7. Verificar la instalación desde una **copia limpia** del repositorio utilizando exclusivamente el README: entorno, configuración, migraciones, seeders, servidor, endpoints.

## 7. Criterios pendientes para el cierre

- [x] Consultar recursos con 200.
- [x] Crear un recurso con 201.
- [x] Verificar inexistente con 404.
- [x] Rechazar datos inválidos con 422.
- [x] Probar y documentar duplicado (encontrado defecto 500).
- [x] Modificar un equipamiento mediante PATCH.
- [x] Verificar orden y paginación.
- [x] Ejecutar consulta combinada con filtro, orden y paginación.
- [x] Verificar datos tras reiniciar la API.
- [x] Validar coherencia temporal en reservas con 422.
- [x] Verificar choque horario entre reservas confirmadas (409, CP-11).
- [x] Probar fechas iguales (422 reportado; CP-12 sin captura).
- [ ] Acreditar una respuesta 400 para una regla de negocio real, si corresponde.

## 8. Conclusión

Se ejecutaron múltiples pruebas reales en Swagger que demuestran consultas exitosas, creación, actualización, validaciones, manejo de no encontrados y conservación de datos después de reiniciar la API. También se registró un error confirmado de manejo de correo duplicado y una posible omisión de la restricción de capacidad. Se registran error al intentar 409, dando 500.

## 9. Qué falta para cerrar el entregable del área

**Indispensable según la pauta:** (a) convertir las solicitudes en un archivo `.http` o colección Postman/Thunder Client que pueda repetirse sin editar código fuente; (b) registrar los resultados esperado/obtenido con pruebas que aíslen o restauren datos; (c) comprobar desde una copia limpia que el README permite preparar BD, migraciones, seeders, iniciar API y repetir pruebas; (d) conservar evidencia del conflicto 409, ya agregada aquí; (e) verificar que la API/documentación final cumpla respuestas uniformes y reglas de negocio.



**Contribución Git:** cada integrante debe disponer de cinco commits significativos propios, una rama diferente de `main` y al menos un pull request; hay que comprobarlo en el repositorio antes de la entrega.

