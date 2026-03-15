[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/AG7uuOyW)


Esta actividad fue hecha por mi en conjunto con Claude Opus 4.6

Primero le dí los pdfs de las clases y que me haga un resumen de la materia, para apoyarme y reforzar lo visto en clases. 

Luego le expliqué el enunciado de la actividad, le pase el repositorio con el código inicial de la tarea y le explique que no toque nada, que entienda las funciones nada mas y así poder preguntarle en caso de que no entienda. 

Luego le pedí ayuda a generar los tests que fuimos haciendo en conjunto e hicimos 35 tests que corrieron con coverage total, siguiendo los principios FIRST.

Con esta herramienta aprendí mucho de cómo  lograr todo el coverage cuando quiero testear el código.

Cuando corrí el repo, se generó el archivo .coverage en windows, pero luego por algún motivo despupes me decía error. Por lo tanto le pedí a claude que me ayude a que corra el código y que el criterio de coverage sea exactamente el mismo que requería originalmente. Me creó un archivo llamado .coveragerc que luego me explicó que hacía. Hace lo siguiente:

".coverage vs .coveragerc

  - .coverage — es una base de datos SQLite que guarda los resultados de correr coverage run. Se regenera cada vez que
  ejecutas los tests. NO es un archivo de configuración.
  - .coveragerc — es el archivo de configuración que le dice a coverage cómo medir (con branches, qué archivos incluir,
  etc.).

  El .coverage que ya existía en tu repo fue generado en Windows en una corrida anterior. Al mirar sus datos internos veo
  has_arcs=1, lo que significa que esa corrida sí midió branch coverage. Mi .coveragerc tiene branch = true, así que sí,
  usan el mismo criterio.

  El .coveragerc que creé es necesario porque el notebook ejecuta:
  coverage run --rcfile=.coveragerc -m unittest discover -s tests

  Sin ese archivo, coverage no activaría branch coverage por defecto, y el reporte no mostraría las columnas Branch y BrPart
   que espera la evaluación."