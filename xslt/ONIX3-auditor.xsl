<?xml version="1.0" encoding="UTF-8"?>


<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns="http://ns.editeur.org/onix/3.0/short"
    exclude-result-prefixes="xs" version="2.0"
    xpath-default-namespace="http://ns.editeur.org/onix/3.0/short">



    <xsl:output method="text" indent="no" encoding="UTF-8"/>


 
  
    <xsl:param name="file_path"
        >/Users/dwh2128/Documents/SimplyE/books/JHU/ONIX/ONIX3_converted/TO-IMPORT/v4/out3/</xsl:param>
        
<!--
    <xsl:param name="file_path">/Users/dwh2128/Documents/SimplyE/books/Casalini/Output/v1/</xsl:param>
 -->
 
    <xsl:variable name="lf"><xsl:text>&#10;</xsl:text></xsl:variable>
    <xsl:variable name="delim1">|</xsl:variable>
    <xsl:variable name="delim2">;</xsl:variable>    
    

    <xsl:variable name="heads">FILE|ID|BIBID|ISBN|FORMAT|descriptivedetail/titledetail/titleelement/b203|descriptivedetail /titledetail/ titleelement/b030 |descriptivedetail /titledetail /titleelement /b031|descriptivedetail /titledetail /titleelement /b029|count(descriptivedetail /language /b252)|count(publishingdetail /publisher /b081)|count(publishingdetail /imprint /b079)|count(b385)|count(descriptivedetail/subject[b067/text() = ('01', '03', '04', '10', '12')]/b069 )|count(descriptivedetail /audience /b204[text = ('01', '02', '03', '04', '05', '06', '07', '08', '09')] )|"count(descriptivedetail /contributor /(b036|b037|b040|b044) )"|"count(collateraldetail/textcontent[x426 = '03']/d104 )"|DESCRIPTION CHARS|"count(descriptivedetail /epubusageconstraint /x319 )"|"count(descriptivedetail /epubusageconstraint /epubusagelimit /(x321|x320) )"</xsl:variable>
    
    <xsl:template match="/">
        
        <xsl:value-of select="$heads"/>
        <xsl:value-of select="$lf"/>
        

        <xsl:for-each select="collection(concat($file_path, '?select=*.xml;recurse=yes'))">
  
            <xsl:variable name="mypath" select="tokenize(base-uri(),'/')"/>
    
            <xsl:variable name="filename">
                <xsl:value-of select="substring-before( $mypath[last()], '.xml')"/>
            </xsl:variable>

            <xsl:apply-templates select="/ONIXmessage/product">
                <xsl:with-param name="filename" select="$filename"/>
            </xsl:apply-templates>
            
        
        </xsl:for-each>


    </xsl:template>

    <xsl:template match="b333">
        <xsl:choose>
            <xsl:when test="text() = 'E101'">EPUB</xsl:when>
            <xsl:when test="text() = 'E107'">PDF</xsl:when>
            <xsl:otherwise>UNKNOWN</xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="product">
        <xsl:param name="filename"/>

        <xsl:variable name="bibid">
            <xsl:analyze-string select="collateraldetail/textcontent[x426 = '03'][last()]/d104" regex="/catalog/(\d+)">
                <xsl:matching-substring>
                    <xsl:value-of select="regex-group(1)"/>
                </xsl:matching-substring>
            </xsl:analyze-string>
        </xsl:variable>
        
<!--  Warning reports.      -->
        <xsl:if test="$bibid = ''">
            <xsl:message>WARNING: No BIBID in product <xsl:value-of select="a001"/> (<xsl:value-of select="$filename"/>). </xsl:message>
        </xsl:if>
        <xsl:if test="not(descriptivedetail/titledetail/titleelement/b203 or
            (descriptivedetail/titledetail/titleelement/b030
            and descriptivedetail/titledetail/titleelement/b031 ))">
            <xsl:message>WARNING: Title missing or incomplete in product <xsl:value-of select="a001"/> (<xsl:value-of select="$filename"/>). </xsl:message>
        </xsl:if>
        <xsl:if test="not(productidentifier[1]/b244)">
            <xsl:message>WARNING: No ISBN in product <xsl:value-of select="a001"/> (<xsl:value-of select="$filename"/>). </xsl:message>
        </xsl:if>
        <xsl:if test="not(descriptivedetail/language/b252)">
            <xsl:message>WARNING: No LANGUAGE in product <xsl:value-of select="a001"/> (<xsl:value-of select="$filename"/>). </xsl:message>
        </xsl:if>
        <xsl:if test="not(publishingdetail/publisher/b081)">
            <xsl:message>WARNING: No PUBLISHER in product <xsl:value-of select="a001"/> (<xsl:value-of select="$filename"/>). </xsl:message>
        </xsl:if>
        <xsl:if test="not(descriptivedetail/subject[b067/text() = ('01', '03', '04', '10', '12')]/b069)">
            <xsl:message>WARNING: No SUBJECT CODES in product <xsl:value-of select="a001"/> (<xsl:value-of select="$filename"/>). </xsl:message>
        </xsl:if>
        <xsl:if test="not(descriptivedetail/contributor/(b036|b037|b040|b044))">
            <xsl:message>WARNING: No CONTRIBUTORS in product <xsl:value-of select="a001"/> (<xsl:value-of select="$filename"/>). </xsl:message>
        </xsl:if>
        <xsl:if test="not(collateraldetail/textcontent[x426 = '03']/d104 )">
            <xsl:message>WARNING: No SUMMARY in product <xsl:value-of select="a001"/> (<xsl:value-of select="$filename"/>). </xsl:message>
        </xsl:if>
      
      
<!--  OUTPUT info to csv      -->
        

        <xsl:value-of select="$filename"/>
        <xsl:value-of select="$delim1"/>
        <xsl:value-of select="a001"/>  <!-- product ID -->
        <xsl:value-of select="$delim1"/>
        <xsl:value-of select="$bibid"/>
        <xsl:value-of select="$delim1"/>
        <xsl:value-of select="productidentifier[1]/b244"/>  <!-- ISBN -->
        <xsl:value-of select="$delim1"/>
        <xsl:apply-templates select="descriptivedetail/b333"/> <!-- EPUB or PDF -->
        <xsl:value-of select="$delim1"/>
        <xsl:value-of select="normalize-space(descriptivedetail/titledetail/titleelement/b203)"/>  <!-- Title -->
        <xsl:value-of select="$delim1"/>
        <xsl:value-of select="normalize-space(descriptivedetail/titledetail/titleelement/b030)"/>
        <xsl:value-of select="$delim1"/>
        <xsl:value-of select="normalize-space(descriptivedetail/titledetail/titleelement/b031)"/>
        <xsl:value-of select="$delim1"/>
        <xsl:value-of select="normalize-space(descriptivedetail/titledetail/titleelement/b029)"/>
        <xsl:value-of select="$delim1"/>
        <xsl:value-of select="count(descriptivedetail/language/b252)"/>
        <xsl:value-of select="$delim1"/>
        <xsl:value-of select="count(publishingdetail/publisher/b081)"/>
        <xsl:value-of select="$delim1"/>
        <xsl:value-of select="count(publishingdetail/imprint/b079)"/>
        <xsl:value-of select="$delim1"/>
        <xsl:value-of select="count(b385)"/>
        <xsl:value-of select="$delim1"/>
        <xsl:value-of select="count(descriptivedetail/subject[b067/text() = ('01', '03', '04', '10', '12')]/b069 )"/>
        <xsl:value-of select="$delim1"/>
        <xsl:value-of select="count(descriptivedetail/audience/b204[text() = ('01', '02', '03', '04', '05', '06', '07', '08', '09')] )"/>
        <xsl:value-of select="$delim1"/>
        <xsl:value-of select="count(descriptivedetail/contributor/(b036|b037|b040|b044) )"/>
        <xsl:value-of select="$delim1"/>
        <xsl:value-of select="count(collateraldetail/textcontent[x426 = '03']/d104 )"/>
        <xsl:value-of select="$delim1"/>
        <xsl:value-of select="sum(collateraldetail/textcontent[x426 = '03']/d104/descendant-or-self::text()/string-length(normalize-space(.)))"/>
        <xsl:value-of select="$delim1"/>
        <xsl:value-of select="count(descriptivedetail/epubusageconstraint/x319 )"/>
        <xsl:value-of select="$delim1"/>
        <xsl:value-of select="count(descriptivedetail/epubusageconstraint/epubusagelimit/(x321|x320) )"/>


        <xsl:value-of select="$lf"/>
    </xsl:template>

</xsl:stylesheet>
