<?xml version="1.0" encoding="UTF-8"?>
<!-- List all of the ISBNS found in ONIX3 files in a given directory. -->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs"
    version="2.0"
     xpath-default-namespace="http://ns.editeur.org/onix/3.0/short"
    >
    
    <xsl:output method="text"/>
    
    <xsl:param name="base_url">https://academic.lyrasistechnology.org/columbia/book/https%3A%2F%2Fcolumbia.lyrasistechnology.org%2F190150%2Fworks%2FISBN%2F</xsl:param>
    
     
    <xsl:param name="input_dir">/Users/dwh2128/Documents/SimplyE/books/JHU/ONIX/ONIX3_converted/TO-IMPORT/v3/</xsl:param> 
    <xsl:param name="publisher">[Provide Publisher Here]</xsl:param> 
    
  <xsl:variable name="heads">BIBID|VENDOR|PUBLISHER|TITLE|ISBN|HREF</xsl:variable>
  
    <xsl:variable name="delim">
        <xsl:text>|</xsl:text>
    </xsl:variable>  
    <xsl:variable name="lf">
        <xsl:text>
</xsl:text>
    </xsl:variable>
        
    <xsl:template match="/">
        
        <xsl:value-of select="$heads"/>
        <xsl:value-of select="$lf"></xsl:value-of>
        

        <xsl:for-each select="collection(concat($input_dir, '?select=*.xml;recurse=yes'))">

        <xsl:apply-templates select="ONIXmessage/product"/>
        
        </xsl:for-each>

    </xsl:template>
    
    <xsl:template match="product">

        <xsl:variable name="bibid">
            <xsl:analyze-string select="collateraldetail/textcontent/d104" regex="/catalog/(\d+)">
                <xsl:matching-substring>
                    <xsl:value-of select="regex-group(1)"/>
                </xsl:matching-substring>
            </xsl:analyze-string>
        </xsl:variable>
        
        <xsl:if test="normalize-space($bibid)">

            
          <!--  BIBID      -->
          <xsl:value-of select="$bibid"/>
          <xsl:value-of select="$delim"/>
          
            <!--  VENDOR      -->
            <xsl:value-of select="$publisher"/>
            <xsl:value-of select="$delim"/>

            <!--  PUBLISHER      -->
          <xsl:value-of select="$publisher"/>
          <xsl:value-of select="$delim"/>
 
            <!--  TITLE      -->
            <xsl:value-of select="descriptivedetail/titledetail[1]/titleelement[1]/b203"/>
            <xsl:value-of select="$delim"/>

            <!--  ISBN      -->
            <xsl:value-of select="a001"/>
            <xsl:value-of select="$delim"/>
            
            
          <!--  HREF      -->
          <xsl:value-of select="concat($base_url, a001)"/>
          
          <xsl:value-of select="$lf"/>
            
        </xsl:if>
        
    </xsl:template>
    
</xsl:stylesheet>