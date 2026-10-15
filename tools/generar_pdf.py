# -*- coding: utf-8 -*-
"""
Genera assets/docs/Guia_Conexion_Datasphere_Informix_Publica.pdf — la version
imprimible del articulo blog/informix-sap-datasphere-generic-jdbc.html.

El PDF se construye desde aqui para que no quede como un binario huerfano:
cuando el articulo cambie, se edita este archivo y se vuelve a generar.

    pip install reportlab pillow
    python tools/generar_pdf.py

Estilo: A4, margenes de 2 cm, Helvetica para el texto, Courier para el codigo
y el azul #0a4a8c para titulos — los mismos de la primera version del PDF.
"""

import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    Image, PageBreak, Paragraph, Preformatted, SimpleDocTemplate, Spacer, Table,
    TableStyle,
)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "assets", "docs", "Guia_Conexion_Datasphere_Informix_Publica.pdf")
CAPTURA = os.path.join(RAIZ, "assets", "img", "datasphere-informix-conexion.png")

TITULO = u"Guía de conexión SAP Datasphere – Informix"
PIE = u"Guía de conexión SAP Datasphere – Informix (Generic JDBC)"

AZUL = colors.Color(0.039216, 0.290196, 0.54902)       # #0a4a8c
GRIS = colors.Color(0.333333, 0.333333, 0.333333)
GRIS_PIE = colors.Color(0.533333, 0.533333, 0.533333)
FONDO_TABLA = colors.Color(0.917647, 0.945098, 0.972549)
LINEA = colors.Color(0.80, 0.84, 0.88)

ANCHO_UTIL = A4[0] - 4 * cm - 12          # margenes de 2 cm + el padding del Frame

# ---------------------------------------------------------------- estilos
_base = getSampleStyleSheet()

E = {
    "titulo": ParagraphStyle(
        "titulo", parent=_base["Title"], fontName="Helvetica-Bold",
        fontSize=20, leading=24, textColor=AZUL, alignment=TA_CENTER, spaceAfter=0),
    "subtitulo": ParagraphStyle(
        "subtitulo", parent=_base["Normal"], fontName="Helvetica",
        fontSize=10, leading=12, textColor=GRIS, alignment=TA_CENTER),
    "seccion": ParagraphStyle(
        "seccion", parent=_base["Heading2"], fontName="Helvetica-Bold",
        fontSize=13.5, leading=18, textColor=AZUL, spaceBefore=14, spaceAfter=6),
    "cuerpo": ParagraphStyle(
        "cuerpo", parent=_base["Normal"], fontName="Helvetica",
        fontSize=10, leading=14, alignment=TA_JUSTIFY, spaceAfter=6),
    "vineta": ParagraphStyle(
        "vineta", parent=_base["Normal"], fontName="Helvetica",
        fontSize=10, leading=14, leftIndent=14, bulletIndent=2, spaceAfter=4),
    "paso": ParagraphStyle(
        "paso", parent=_base["Normal"], fontName="Helvetica",
        fontSize=10, leading=14, leftIndent=16, bulletIndent=2,
        bulletFontName="Helvetica-Bold", spaceAfter=4),
    "celda": ParagraphStyle(
        "celda", parent=_base["Normal"], fontName="Helvetica", fontSize=9, leading=12),
    "celda_cabecera": ParagraphStyle(
        "celda_cabecera", parent=_base["Normal"], fontName="Helvetica-Bold",
        fontSize=9, leading=12),
    "celda_codigo": ParagraphStyle(
        "celda_codigo", parent=_base["Normal"], fontName="Courier", fontSize=8.5, leading=11),
    "codigo": ParagraphStyle(
        "codigo", parent=_base["Code"], fontName="Courier", fontSize=8.8,
        leading=12, leftIndent=10, spaceBefore=2, spaceAfter=8),
    "pie_figura": ParagraphStyle(
        "pie_figura", parent=_base["Normal"], fontName="Helvetica", fontSize=8.5,
        leading=11, textColor=GRIS, alignment=TA_CENTER, spaceBefore=6),
    "fuente": ParagraphStyle(
        "fuente", parent=_base["Normal"], fontName="Helvetica", fontSize=8.5,
        leading=11, leftIndent=14, bulletIndent=2, spaceAfter=5),
}


def p(texto, estilo="cuerpo", **kw):
    return Paragraph(texto, E[estilo], **kw)


def vineta(texto, estilo="vineta"):
    return Paragraph(texto, E[estilo], bulletText=u"•")


def paso(numero, texto):
    return Paragraph(texto, E["paso"], bulletText=str(numero))


def tabla(filas, anchos, codigo_en=()):
    """filas[0] es la cabecera. codigo_en = indices de columna en Courier."""
    datos = [[p(c, "celda_cabecera") for c in filas[0]]]
    for fila in filas[1:]:
        datos.append([
            p(celda, "celda_codigo" if i in codigo_en else "celda")
            for i, celda in enumerate(fila)
        ])
    t = Table(datos, colWidths=anchos, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), FONDO_TABLA),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINEA),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def c(texto):
    """Codigo en linea dentro de un parrafo."""
    return u'<font face="Courier">%s</font>' % texto


def b(texto):
    return u"<b>%s</b>" % texto


# ---------------------------------------------------------------- contenido
def contenido():
    f = []
    f.append(p(u"Conexión de SAP Datasphere a Informix", "titulo"))
    f.append(Spacer(1, 6))
    f.append(p(u"Guía de preparación vía Generic JDBC y Data Provisioning Agent · "
               u"Octubre 2026", "subtitulo"))

    # 1
    f.append(p(u"1. Resumen", "seccion"))
    f.append(p(
        u"Informix (IBM / HCL) no tiene un conector nativo en Datasphere; se conecta con el "
        u"tipo %s, que se ejecuta sobre el adaptador %s del %s on-premise. El agente debe "
        u"tener red hacia el servidor Informix y tener instalado el driver JDBC de Informix. "
        u"Mientras no se seleccione un agente, la función <i>Tablas remotas</i> aparece como "
        u"<i>Deshabilitado</i>."
        % (b(u"Generic JDBC"), b(u"CamelJdbcAdapter"),
           b(u"Data Provisioning Agent (DP Agent)"))))

    # 2
    f.append(p(u"2. Datos a solicitar", "seccion"))
    f.append(tabla([
        [u"A quién", u"Qué"],
        [u"Admin de Informix",
         u"Host/IP y puerto del listener (onsoctcp); nombre de la base de datos; nombre de "
         u"la instancia %s (archivo sqlhosts); usuario de lectura (CONNECT + SELECT); locale "
         u"de la base (DB_LOCALE) si hay tildes/ñ; versión de Informix." % b(u"INFORMIXSERVER")],
        [u"Infraestructura / redes",
         u"Que el servidor del DP Agent llegue al host y puerto de Informix (firewall "
         u"abierto). Prueba desde PowerShell en el servidor del agente: %s (debe devolver "
         u"%s)."
         % (c(u"Test-NetConnection -ComputerName &lt;IPInformixDatabase&gt; -Port &lt;PortDB&gt;"),
            c(u"TcpTestSucceeded : True"))],
    ], anchos=[4 * cm, ANCHO_UTIL - 4 * cm]))

    # 3
    f.append(p(u"3. Descargar el driver JDBC y su dependencia BSON", "seccion"))
    f.append(p(
        u"El driver no lo entrega SAP; se descarga de IBM/HCL o de Maven Central. Los drivers "
        u'4.50.x dependen de la librería %s (MongoDB), que tiene su propia numeración: no '
        u'existe un "bson 4.50". La versión que declaran los drivers 4.50 es %s.'
        % (b(u"bson"), b(u"bson 3.8.0"))))
    f.append(tabla([
        [u"Archivo", u"Dónde descargarlo"],
        [u"jdbc-4.50.x.jar (driver Informix)",
         u"Maven Central: %s<br/>https://mvnrepository.com/artifact/com.ibm.informix/jdbc<br/>"
         u"Alternativas: %s en el servidor Informix, o el portal de descargas de HCL."
         % (c(u"com.ibm.informix:jdbc"), c(u"$INFORMIXDIR/jdbc/lib/ifxjdbc.jar"))],
        [u"bson-3.8.0.jar (dependencia)",
         u"Maven Central: %s<br/>https://mvnrepository.com/artifact/org.mongodb/bson/3.8.0"
         % c(u"org.mongodb:bson:3.8.0")],
    ], anchos=[4 * cm, ANCHO_UTIL - 4 * cm]))
    f.append(Spacer(1, 6))
    f.append(p(
        u"Tip: en la página del driver en mvnrepository, la sección <i>Compile Dependencies</i> "
        u"muestra la versión exacta de bson que pide. Si falta el bson, el error típico es %s."
        % c(u"ClassNotFoundException: org.bson.BSONObject")))

    # 4
    f.append(p(u"4. Preparar el DP Agent", "seccion"))
    f.append(paso(1, u"Instalar el DP Agent y registrarlo en Datasphere: "
                     u"<i>Configuración del sistema → Integración de datos → "
                     u"Agentes on-premise</i>."))
    f.append(paso(2, u"En %s, verificar la entrada %s. La documentación de SDI indica "
                     u"descomentarla; en versiones recientes del agente ya viene activa. "
                     u"Debe existir %s entrada, sin bloques viejos o duplicados."
                     % (c(u"&lt;DPAgent_root&gt;/camel/adapters.xml"),
                        c(u'&lt;Adapter type="CamelJdbcAdapter" ...&gt;'),
                        b(u"una sola"))))
    f.append(paso(3, u"Copiar %s y %s en %s (Windows: %s; Linux: %s)."
                     % (c(u"jdbc-4.50.x.jar"), c(u"bson-3.8.0.jar"),
                        c(u"&lt;DPAgent_root&gt;/camel/lib/"),
                        c(u"C:\\usr\\sap\\dataprovagent\\"),
                        c(u"/usr/sap/dataprovagent/"))))
    f.append(paso(4, u"Reiniciar el DP Agent."))
    f.append(paso(5, u"En Datasphere, en el agente, habilitar %s y confirmar que el agente "
                     u"está <i>Conectado</i>. Si se modificó adapters.xml, deshabilitar y "
                     u"volver a habilitar el adaptador para reregistrarlo." % b(u"CamelJdbcAdapter")))
    f.append(Spacer(1, 6))
    f.append(p(u"Estructura esperada de la carpeta:"))
    f.append(Preformatted(u"camel/lib/\n  |-- jdbc-4.50.x.jar\n  `-- bson-3.8.0.jar", E["codigo"]))

    # 5
    f.append(p(u"5. Crear la conexión en Datasphere", "seccion"))
    f.append(p(u"En el espacio: <i>Conexiones → Crear → Generic JDBC (JDBC genérico)</i>."))
    f.append(tabla([
        [u"Campo", u"Valor"],
        [u"Clase de controlador JDBC", c(u"com.informix.jdbc.IfxDriver")],
        [u"URL JDBC",
         c(u"jdbc:informix-sqli://&lt;host&gt;:&lt;puerto&gt;/&lt;base_datos&gt;:"
           u"INFORMIXSERVER=&lt;instancia&gt;")],
        [u"Nombre de usuario / Contraseña",
         u"Usuario de lectura entregado por el admin de Informix"],
        [u"Agente de aprovisionamiento de datos",
         u"El DP Agent donde se habilitó CamelJdbcAdapter"],
        [u"Nombre de la empresa / técnico", u"Nombre libre que identifique la conexión"],
    ], anchos=[5.2 * cm, ANCHO_UTIL - 5.2 * cm]))
    f.append(Spacer(1, 8))
    f.append(p(u"Ejemplo con valores ficticios:"))
    f.append(Preformatted(
        u"jdbc:informix-sqli://10.0.0.25:9088/mi_base:INFORMIXSERVER=ol_informix1", E["codigo"]))
    f.append(vineta(u"%s y es el nombre de la instancia (sqlhosts), no el hostname."
                    % b(u"INFORMIXSERVER es obligatorio")))
    f.append(vineta(u"Parámetros opcionales separados por %s, p. ej. %s y %s. %s conviene "
                    u"ponerlo siempre: sin él la tabla remota se crea pero no devuelve datos "
                    u"(sección 6)."
                    % (c(u";"), c(u"DB_LOCALE"), c(u"CLIENT_LOCALE"), c(u"DELIMIDENT=Y"))))
    f.append(vineta(u"No incluir la contraseña en la URL: Datasphere no la almacena cifrada."))
    f.append(vineta(u"La clase del driver se puede confirmar abriendo el jar como .zip: %s."
                    % c(u"META-INF/services/java.sql.Driver")))

    # Figura
    f.append(Spacer(1, 10))
    f.append(p(u"Configuración de referencia en Datasphere:"))
    f.append(figura())
    f.append(p(u"Figura 1. Conexión Generic JDBC configurada, con agente seleccionado y "
               u"Tablas remotas habilitadas. Los datos de servidor, nombres y agente se "
               u"difuminaron.", "pie_figura"))

    # 6 — seccion nueva
    f.append(p(u"6. La tabla remota no muestra los datos", "seccion"))
    f.append(p(u"Con la conexión ya validada y la tabla remota desplegada, la vista previa de "
               u"los datos puede fallar con este mensaje:"))
    f.append(Preformatted(
        u"Error interno: Falló la ejecución de DPAdapterResultSet::Fetch:Camel",
        E["codigo"]))
    f.append(p(u"No es red ni permisos: la conexión ya sirvió para leer el catálogo y crear la "
               u"tabla remota. Lo que falla es el <i>fetch</i> de las filas. Datasphere genera "
               u"el SQL con los nombres de tabla y de columna entre comillas dobles, y el "
               u"driver de Informix solo interpreta las comillas dobles como %s cuando la "
               u"sesión abre con %s. Por defecto el parámetro va en %s, así que esas comillas "
               u"se leen como literales de texto y la consulta se cae del lado de Informix."
               % (b(u"identificadores delimitados"), c(u"DELIMIDENT=Y"), c(u"N"))))
    f.append(p(u"La solución es agregar ese parámetro al final de la URL JDBC de la conexión:"))
    f.append(Preformatted(
        # Preformatted es texto plano: aqui los < > van literales
        u"jdbc:informix-sqli://<host>:<puerto>/<base>:"
        u"INFORMIXSERVER=<servidor>;DELIMIDENT=Y",
        E["codigo"]))
    f.append(p(u"Sobre el ejemplo anterior:"))
    f.append(Preformatted(
        u"jdbc:informix-sqli://10.0.0.25:9088/mi_base:INFORMIXSERVER=ol_informix1;DELIMIDENT=Y",
        E["codigo"]))
    f.append(p(u"Conviene dejar %s desde el primer momento, antes de crear tablas remotas: el "
               u"error no aparece al validar la conexión ni al importar el catálogo, solo al "
               u"leer los datos, y para entonces ya parece un problema de otra cosa. Después "
               u"de editar la URL, guarde la conexión y vuelva a probar la vista previa; si la "
               u"tabla remota sigue fallando, elimínela y vuelva a desplegarla."
               % c(u"DELIMIDENT=Y")))

    # 7
    f.append(p(u"7. Diagnóstico de errores", "seccion"))
    f.append(p(u"Los logs del agente están en %s (%s, %s). Para más detalle, subir el nivel de "
               u"trazas a ALL (KBA 2496051)."
               % (c(u"&lt;DPAgent_root&gt;/log/"), c(u"framework.trc"),
                  c(u"framework_alert.trc"))))
    f.append(tabla([
        [u"Error en framework.trc", u"Causa probable / acción"],
        [c(u"DPAdapterResultSet::Fetch:Camel") +
         u"<br/>(al ver los datos de una tabla remota)",
         u"Falta DELIMIDENT=Y al final de la URL JDBC. Ver la sección 6."],
        [c(u"Cannot create JDBC driver of class '' for connect URL ''"),
         u"La clase y la URL llegan vacías al adaptador: la definición del CamelJdbcAdapter no "
         u"coincide con la que espera Datasphere. Revisar adapters.xml (una sola entrada), "
         u"reiniciar, reregistrar el adaptador y volver a crear la conexión. Verificar versión "
         u"mínima del DP Agent."],
        [c(u"Cannot load JDBC driver class 'com.informix.jdbc.IfxDriver'"),
         u"El jar no está en camel/lib o el agente no se reinició."],
        [c(u"ClassNotFoundException: org.bson.BSONObject"),
         u"Falta bson-3.8.0.jar en camel/lib."],
        [c(u"Connection refused / timeout, o error de INFORMIXSERVER"),
         u"Red/firewall, puerto o nombre de instancia incorrecto en la URL."],
    ], anchos=[6.4 * cm, ANCHO_UTIL - 6.4 * cm]))

    # 8
    f.append(p(u"8. Limitaciones", "seccion"))
    f.append(vineta(u"Generic JDBC soporta tablas remotas (federación y snapshot/replicación "
                    u"programada desde la tabla remota). No soporta replicación en tiempo "
                    u"real, flujos de datos ni flujos de replicación."))
    f.append(vineta(u"Para volúmenes grandes, preferir snapshots programados en lugar de "
                    u"consultas federadas."))

    # 9
    f.append(p(u"9. Fuentes", "seccion"))
    for texto in [
        u"SAP Help – SAP HANA Smart Data Integration (configuración del Camel JDBC Adapter en "
        u"el DP Agent): https://help.sap.com/docs/HANA_SMART_DATA_INTEGRATION/"
        u"7952ef28a6914997abc01745fef1b607/1247c9518f8d4b5b93fa2ad54cb2dcf6.html?locale=en-US",
        u"SAP Blog – Data Provisioning using OracleLogReaderAdapter and CamelJDBCAdapter "
        u"(descomentar CamelJdbcAdapter en adapters.xml y copiar el jar a camel/lib): "
        u"https://blogs.sap.com/2020/09/22/"
        u"data-provisioning-using-oraclelogreaderadapter-and-cameljdbcadapter/",
        u"Driver Informix JDBC (Maven Central): "
        u"https://mvnrepository.com/artifact/com.ibm.informix/jdbc",
        u"BSON 3.8.0 (Maven Central): https://mvnrepository.com/artifact/org.mongodb/bson/3.8.0",
        u"POM del driver 4.50.10 (dependencia bson 3.8.0): https://repository.jboss.org/nexus/"
        u"repository/developer/com/ibm/informix/jdbc/4.50.10/jdbc-4.50.10.pom",
        u"IBM – What's new in Informix JDBC Driver 4.50: "
        u"https://www.ibm.com/docs/SSGU8G_14.1.0/com.ibm.jdbc.doc/ids_jdbc_008.htm",
        u"DbVisualizer – ClassNotFoundException org.bson.BSONObject: "
        u"https://support.dbvis.com/support/solutions/articles/1000283140",
    ]:
        f.append(vineta(texto, "fuente"))

    return f


def figura():
    """La captura, escalada al ancho util."""
    ancho_px, alto_px = ImageReader(CAPTURA).getSize()
    ancho = ANCHO_UTIL
    return Image(CAPTURA, width=ancho, height=ancho * alto_px / float(ancho_px))


def pie_de_pagina(lienzo, doc):
    lienzo.saveState()
    lienzo.setFont("Helvetica", 8)
    lienzo.setFillColor(GRIS_PIE)
    lienzo.drawString(2 * cm, 1.2 * cm, PIE)
    lienzo.drawRightString(A4[0] - 2 * cm, 1.2 * cm, u"Página %d" % doc.page)
    lienzo.restoreState()


def main():
    doc = SimpleDocTemplate(
        SALIDA, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
        title=TITULO, author=u"Christian Escobar Florez",
        subject=u"Conexión Generic JDBC entre SAP Datasphere e IBM Informix",
    )
    doc.build(contenido(), onFirstPage=pie_de_pagina, onLaterPages=pie_de_pagina)
    print(u"PDF generado: %s (%d bytes)" % (SALIDA, os.path.getsize(SALIDA)))


if __name__ == "__main__":
    main()
