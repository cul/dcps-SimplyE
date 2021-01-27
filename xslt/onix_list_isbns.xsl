<?xml version="1.0" encoding="UTF-8"?>
<!-- List all of the ISBNS found in ONIX3 files in a given directory. -->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs"
    version="2.0"
     xpath-default-namespace="http://ns.editeur.org/onix/3.0/short"
    >
    
    <xsl:output method="text"/>
     
    <xsl:param name="input_dir">/Users/dwh2128/Documents/SimplyE/books/JHU/ONIX/ONIX3_converted/TO-IMPORT/v3/</xsl:param> 
    
  
    <xsl:variable name="delim">
        <xsl:text>|</xsl:text>
    </xsl:variable>  
    <xsl:variable name="lf">
        <xsl:text>
</xsl:text>
    </xsl:variable>
        
    <xsl:template match="/">

        <xsl:for-each select="collection(concat($input_dir, '?select=*.xml;recurse=yes'))">

        <xsl:apply-templates select="ONIXmessage/product"/>
        
        </xsl:for-each>

    </xsl:template>
    
    <xsl:template match="product">
<xsl:value-of select="a001"/>
        <xsl:value-of select="$delim"/>
        <xsl:analyze-string select="collateraldetail/textcontent/d104" regex="/catalog/(\d+)">
            <xsl:matching-substring>
                <xsl:value-of select="regex-group(1)"/>
            </xsl:matching-substring>
            
        </xsl:analyze-string>
            <xsl:value-of select="$lf"/>
    </xsl:template>
    
</xsl:stylesheet>