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
    
     
<!--    <xsl:param name="input_dir">/Users/dwh2128/Documents/SimplyE/books/JHU/ONIX/ONIX3_converted/TO-IMPORT/v4/out3/</xsl:param> -->
    <xsl:param name="input_dir">/Users/dwh2128/Documents/SimplyE/dcps-SimplyE/onix/Casalini</xsl:param> 
    <xsl:param name="publisher">[Provide Publisher Here]</xsl:param> 
    
  <xsl:variable name="heads">BIBID|VENDOR|PUBLISHER|TITLE|ISBN|HREF|PDF|EPUB</xsl:variable>
  
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
        
        <!-- Group books by ID to consolidate data from different formats.     -->
        <xsl:for-each-group select="collection(concat($input_dir, '?select=*.xml;recurse=yes'))/ONIXmessage/product" 
            group-by="a001">
            <xsl:sort select="a001"/>
            
            <xsl:variable name="bibid">
            <xsl:choose>
                <xsl:when test="current-group()[1]/collateraldetail/textcontent/d104[contains(., '/catalog/')]">
                        <xsl:analyze-string select="current-group()[1]/collateraldetail/textcontent/d104[contains(., '/catalog/')]" regex="/catalog/(\d+)">
                            <xsl:matching-substring>
                                <xsl:value-of select="regex-group(1)"/>
                            </xsl:matching-substring>
                        </xsl:analyze-string>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:message>*** WARNING: NO BIBID FOUND IN <xsl:value-of select="current-group()[1]/a001"/></xsl:message>
                </xsl:otherwise>
            </xsl:choose>
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

                <xsl:apply-templates select="current-group()[1]/descriptivedetail/titledetail[1]">
    
                </xsl:apply-templates>
                <xsl:value-of select="$delim"/>
                
                <!--  ISBN      -->
                
                <xsl:variable name="isbn">
                <xsl:choose>
                    <xsl:when test="current-group()[1]/productidentifier[b221 = '15']">
                        <xsl:value-of select="current-group()[1]/productidentifier[b221 = '15']/b244"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:value-of select="current-group()[1]/productidentifier[1]/b244"/>
                    </xsl:otherwise>
                </xsl:choose>
 
                </xsl:variable>
                
                <xsl:value-of select="$isbn"/>
                <xsl:value-of select="$delim"/>
                
                
                <!--  HREF      -->
                <xsl:value-of select="concat($base_url, $isbn)"/>
                <xsl:value-of select="$delim"/>
                
                
                <!--  PDF      -->
                <!-- If any b333 for book = E107 then mark as true.     -->
                <xsl:if test="current-group()/descriptivedetail[b333 = 'E107']">Y</xsl:if>
                <xsl:value-of select="$delim"/>            
                
                <!--  EPUB      -->
                <!-- If any b333 for book = E101 then mark as true.     -->
                <xsl:if test="current-group()/descriptivedetail[b333 = 'E101']">Y</xsl:if>
                
                 
                <xsl:value-of select="$lf"/>
                
            </xsl:if>
        </xsl:for-each-group>
        

    </xsl:template>
 
    <xsl:template match="titledetail">
        <xsl:choose>
        <!-- Concatenate title info if there is an article           -->
            <xsl:when test="titleelement/b203">
                <xsl:value-of select="normalize-space(translate(titleelement[1]/b203, '&quot;', ''))"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="normalize-space(translate(titleelement[1]/b030, '&quot;', ''))"/>
                <xsl:text> </xsl:text>
                <xsl:value-of select="normalize-space(translate(titleelement[1]/b031, '&quot;', ''))"/>
            </xsl:otherwise>
        </xsl:choose>
        
        
    </xsl:template>

</xsl:stylesheet>