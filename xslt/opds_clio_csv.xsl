<?xml version="1.0" encoding="UTF-8"?>

<!-- Generate data from sets of OPDS feeds for reporting. 
   Recursively scan $file_path for XML files. -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
   xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs" version="2.0" xpath-default-namespace="http://www.w3.org/2005/Atom">
   <xsl:output method="text" indent="no" encoding="UTF-8"/>

   <xsl:param name="file_path">/Users/dwh2128/Documents/SimplyE/dcps-SimplyE/output/</xsl:param>
   <!--   <xsl:param name="file_path">/Users/dwh2128/Documents/git/dcps-SimplyE/output_test/oapen/books/</xsl:param>-->

   <xsl:param name="site">https://academic.lyrasistechnology.org/columbia</xsl:param>

   <xsl:variable name="base_url">
      <xsl:value-of select="$site"/>
      <xsl:text>/book/https%3A%2F%2Fcolumbia.lyrasistechnology.org%2F190150%2Fworks%2FURI%2F</xsl:text>
   </xsl:variable>


   <xsl:variable name="lf">
      <xsl:text>&#10;</xsl:text>
   </xsl:variable>
   <xsl:variable name="delim1">|</xsl:variable>
   <xsl:variable name="heads">BIBID<xsl:value-of select="$delim1"/>VENDOR<xsl:value-of select="$delim1"/>COLLECTION<xsl:value-of select="$delim1"/>TITLE<xsl:value-of select="$delim1"/>ID<xsl:value-of select="$delim1"/>HREF<xsl:value-of select="$delim1"/>PDF<xsl:value-of select="$delim1"/>EPUB</xsl:variable>
<xsl:template match="/">
<xsl:value-of select="$heads"/>
<xsl:value-of select="$lf"/>
<xsl:for-each select="collection(concat($file_path, '?select=*.xml;recurse=yes'))">
<xsl:variable name="mypath" select="tokenize(base-uri(),'/')"/>
<xsl:variable name="filename">
<xsl:value-of select="$mypath[last()]"/>
</xsl:variable>
<xsl:apply-templates select="feed/entry">
<xsl:with-param name="filename" select="$filename"/>
</xsl:apply-templates>
</xsl:for-each>
</xsl:template>
<xsl:template match="feed/entry">
<xsl:param name="filename"/>
<!--      <xsl:variable name="id" select="tokenize(id,':')[last()]"/>-->
<xsl:variable name="bibid" select="tokenize(*:isReferencedBy/@*:resource,'/')[last()]"/>
<!--
      <xsl:value-of select="$filename"/>
      <xsl:value-of select="$delim1"/>
      -->
<xsl:if test="not(normalize-space($bibid))">
<xsl:message>*** WARNING: NO BIBID FOUND FOR <xsl:value-of select="normalize-space(id)"/>
</xsl:message>
</xsl:if>
<xsl:value-of select="$bibid"/>
<xsl:value-of select="$delim1"/>
<xsl:choose>
<xsl:when test="contains(*:distribution/@ProviderName, 'Internet Archive')">
<xsl:text>Internet Archive</xsl:text>
</xsl:when>
<xsl:otherwise>
<xsl:value-of select="*:distribution/@ProviderName"/>
</xsl:otherwise>
</xsl:choose>
<xsl:value-of select="$delim1"/>
<xsl:value-of select="normalize-space(tokenize(../title, '\|')[1])"/>
<xsl:value-of select="$delim1"/>
<xsl:text>"</xsl:text>
<xsl:value-of select="normalize-space(translate(title, '\&quot;', ''))"/>
<xsl:text>"</xsl:text>
<xsl:value-of select="$delim1"/>
<xsl:value-of select="normalize-space(id)"/>
<xsl:value-of select="$delim1"/>
<xsl:value-of select="$base_url"/>
<xsl:value-of select="encode-for-uri(id)"/>
<xsl:value-of select="$delim1"/>
<xsl:if test="link[@type='application/pdf']">Y</xsl:if>
<xsl:value-of select="$delim1"/>
<xsl:if test="link[@type='application/epub+zip']">Y</xsl:if>
<!--      <xsl:value-of select="$delim1"/>
      <xsl:value-of select="normalize-space(*:issued)"/>-->
<xsl:value-of select="$lf"/>
</xsl:template>
</xsl:stylesheet>
