# Matriz de estado de la retroalimentaciÃ³n

| ID | ObservaciÃ³n | Estado | Evidencia |
|---|---|---|---|
| O1 | 18 operaciones, solo 8 funcionan | resuelta | `1b4c902`, captura `03-reservas-200.png` |
| O2 | Archivo de diagrama vacÃ­o | resuelta | `2ea6f14`, `25359ed` |
| O3 | Regla de equipamiento daÃ±ado no invocada | resuelta | `a761e10`, prueba `test_equipamiento_danado_impide_confirmar` |
| O4 | `TypeError` como 500 en texto plano | resuelta | `f4f92d1`, `e4e47ea` |
| O5 | Evidencia desactualizada | parcial | `a152ad4`; faltan 7 capturas de 12 |
| O6 | MÃ¡s de 5 endpoints incumplen contrato | resuelta | `b7ae618`, `d1e9ac8` |
| O7 | AutenticaciÃ³n, recuperaciÃ³n, contenedores, CI y pruebas | parcial | `a97b693`, `e4e47ea`, `74d9e73`, `d14ab49`; falta despliegue en Kubero |