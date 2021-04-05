<?xml version="1.0" encoding="UTF-8"?>
<!-- Stylesheet to merge ONIX3-short with list of bibids and produce chunked output. -->
<!-- This version also chunks into 100 products per file. -->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns="http://ns.editeur.org/onix/3.0/short"
    exclude-result-prefixes="xs foo" version="2.0"
    xpath-default-namespace="http://ns.editeur.org/onix/3.0/short"
    xmlns:foo="https://library.columbia.edu/lookup">



    <xsl:output method="xml" omit-xml-declaration="no"
        doctype-system="ONIX_BookProduct_DTDs+codes_Issue_51/ONIX_BookProduct_3.0_short.dtd"
        indent="yes" encoding="UTF-8"/>

    <xsl:variable name="my_name">ONIX3-merge-bibids3.xsl</xsl:variable>

    <xsl:param name="batch_size">100</xsl:param>

    <!-- Values: 'tor' = Torrossa | 'jhup' = Johns Hopkins -->
    <!-- <xsl:param name="publisher">jhup</xsl:param>  -->
    <xsl:param name="publisher">tor</xsl:param>
    <!-- TODO: Make this not necessary!   -->

    <!--    <xsl:param name="out_path"
        >/Users/dwh2128/Documents/SimplyE/books/JHU/ONIX/ONIX3_converted/TO-IMPORT/v4/out4/</xsl:param> -->
    <xsl:param name="out_path"
        >/Users/dwh2128/Documents/SimplyE/books/Casalini/Output/v1/</xsl:param>

    <xsl:param name="isbn_type"/>
    <!--    <xsl:param name="isbn_type">ISBN-13</xsl:param>-->
    <!-- <xsl:param name="isbn_type">ISBN-10</xsl:param>-->

    <xsl:param name="lookup_path"
        >/Users/dwh2128/Documents/SimplyE/books/Casalini/torrossa_isbn_lookup.xml</xsl:param>

    <!--   <xsl:param name="lookup_path"
        >/Users/dwh2128/Documents/SimplyE/books/JHU/ONIX/jhu_isbn_lookup2.xml</xsl:param>-->

    <!-- Import lookup to obtain bibids from isbn. See SET-36.   -->
    <xsl:variable name="isbn_lookup">
        <xsl:copy-of select="document($lookup_path)"/>
    </xsl:variable>


    <xsl:template match="/">

        <xsl:variable name="mypath" select="tokenize(base-uri(),'/')"/>

        <xsl:variable name="filename">
            <xsl:value-of select="substring-before( $mypath[last()], '.xml')"/>
        </xsl:variable>


        <xsl:for-each-group group-by="(position() - 1) idiv $batch_size"
            select="ONIXmessage/product">
            <xsl:result-document href="{$out_path}/{$filename}_OUT_p{position()}.xml" method="xml">
                <xsl:comment>Document generated from source <xsl:value-of select="$filename"/>.xml using stylesheet <xsl:value-of select="$my_name"/> on <xsl:value-of select="current-date()"/>. </xsl:comment>
                <ONIXmessage release="3.0">
                    <xsl:apply-templates select="../header"/>
                    <xsl:apply-templates select="current-group()"/>
                </ONIXmessage>
            </xsl:result-document>
        </xsl:for-each-group>


    </xsl:template>


    <!-- identity transform. -->
    <xsl:template match="@*|node()">
        <xsl:param name="bibid"/>
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()">
                <xsl:with-param name="bibid" select="$bibid"/>
            </xsl:apply-templates>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="@refname | @shortname">
        <!-- omit attributes brought in from DTD in result elements. -->
    </xsl:template>


    <xsl:template match="product">
        <xsl:variable name="isbn">
            <xsl:choose>
                <xsl:when test="$isbn_type = 'ISBN-10'">
                    <xsl:value-of select="productidentifier[b221 = '02']/b244"/>
                </xsl:when>
                <xsl:when test="$isbn_type = 'ISBN-13'">
                    <!-- ISBN-13 format.    -->
                    <xsl:value-of select="productidentifier[b221 = '15']/b244"/>
                </xsl:when>
                <xsl:otherwise>
                    <!-- No global ISBN format set, just take the first (and hopefully only) one! -->
                    <xsl:value-of select="productidentifier[1]/b244"/>
                </xsl:otherwise>
            </xsl:choose>

        </xsl:variable>
        <xsl:variable name="bibid">
            <xsl:value-of select="$isbn_lookup/foo:lookup/foo:record[foo:isbn=$isbn]/foo:bibid"/>
        </xsl:variable>


        <xsl:message>ISBN: <xsl:value-of select="$isbn"/> | BIBID: <xsl:value-of select="$bibid"
            /></xsl:message>

        <xsl:if test="$bibid != ''">
            <!-- ignore records that don't have an associated bibid -->
            <xsl:copy copy-namespaces="no">
                <xsl:apply-templates select="@*|node()">
                    <xsl:with-param name="isbn" select="$isbn"/>
                    <xsl:with-param name="bibid" select="$bibid"/>
                </xsl:apply-templates>
            </xsl:copy>
        </xsl:if>
    </xsl:template>

    <xsl:template match="collateraldetail">
        <xsl:param name="bibid"/>
        <collateraldetail>
            <xsl:choose>
                <xsl:when test="textcontent">
                    <xsl:apply-templates select="textcontent">
                        <xsl:with-param name="bibid" select="$bibid"/>
                    </xsl:apply-templates>
                </xsl:when>
                <xsl:otherwise>

                    <xsl:comment>Warning: No textcontent found!</xsl:comment>
                    <textcontent>
                        <x426>03</x426>
                        <x427>00</x427>
                        <d104>
                            <xsl:text> &lt;P&gt;&lt;a href="https://clio.columbia.edu/catalog/</xsl:text>
                            <xsl:value-of select="$bibid"/>
                            <xsl:text>"&gt;Go to catalog record in CLIO.&lt;/a&gt;&lt;/P&gt;</xsl:text>
                        </d104>
                    </textcontent>

                </xsl:otherwise>
            </xsl:choose>
        </collateraldetail>
    </xsl:template>

    <!-- Process the book description, including adding link to CLIO -->
    <!-- Note: JHUP uses x426 type 01 ("sender-defined text") for description, rather than 03. -->
    <!-- TODO: better logic to determine where the description is. -->
    <!-- See code list: https://www.hanmoto.com/pub/onix/codelists/onix-codelist-153.htm -->
    <xsl:template match="collateraldetail/textcontent">
        <xsl:param name="bibid"/>

        <!--        <xsl:message>$bibid = <xsl:value-of select="$bibid"/></xsl:message>-->

        <xsl:variable name="clio_link">
            <xsl:text> &lt;P&gt;&lt;a href="https://clio.columbia.edu/catalog/</xsl:text>
            <xsl:value-of select="$bibid"/>
            <xsl:text>"&gt;Go to catalog record in CLIO.&lt;/a&gt;&lt;/P&gt;</xsl:text>
        </xsl:variable>

        <xsl:choose>
            <xsl:when test="$publisher = 'jhup'">
                <xsl:if
                    test="x426 = '03' or (x426='01' and not(following-sibling::textcontent[x426='03']))">

                    <textcontent>
                        <x426>03</x426>
                        <x427>00</x427>
                        <d104>
                            <!-- Fix em dashes and other garbled characters -->
                            <xsl:analyze-string select="d104" regex="(â€”|Ã¢â‚¬â€\?)">
                                <xsl:matching-substring>—</xsl:matching-substring>
                                <xsl:non-matching-substring>
                                    <xsl:analyze-string select="." regex="Ã©">
                                        <xsl:matching-substring>é</xsl:matching-substring>
                                        <xsl:non-matching-substring>
                                            <xsl:analyze-string select="." regex="â€™">
                                                <xsl:matching-substring>’</xsl:matching-substring>
                                                <xsl:non-matching-substring>
                                                  <xsl:value-of select="."/>
                                                </xsl:non-matching-substring>
                                            </xsl:analyze-string>
                                        </xsl:non-matching-substring>
                                    </xsl:analyze-string>
                                </xsl:non-matching-substring>
                            </xsl:analyze-string>


                            <xsl:value-of select="$clio_link"/>

                        </d104>
                    </textcontent>

                </xsl:if>

            </xsl:when>

            <xsl:when test="$publisher = 'tor'">

                <xsl:if test="x426 = ('03', '11')">

                    <textcontent>
                        <x426>03</x426>
                        <x427>00</x427>
                        <d104>
                            <!-- Fix em dashes and other garbled characters -->
                            <xsl:analyze-string select="d104" regex="(â€”|Ã¢â‚¬â€\?)">
                                <xsl:matching-substring>—</xsl:matching-substring>
                                <xsl:non-matching-substring>
                                    <xsl:analyze-string select="." regex="Ã©">
                                        <xsl:matching-substring>é</xsl:matching-substring>
                                        <xsl:non-matching-substring>
                                            <xsl:analyze-string select="." regex="â€™">
                                                <xsl:matching-substring>’</xsl:matching-substring>
                                                <xsl:non-matching-substring>
                                                  <xsl:value-of select="."/>
                                                </xsl:non-matching-substring>
                                            </xsl:analyze-string>
                                        </xsl:non-matching-substring>
                                    </xsl:analyze-string>
                                </xsl:non-matching-substring>
                            </xsl:analyze-string>

                            <xsl:if test="not(following-sibling::textcontent[x426=('03', '11')])">
                                <xsl:value-of select="$clio_link"/>

                            </xsl:if>

                        </d104>
                    </textcontent>

                </xsl:if>

            </xsl:when>
        </xsl:choose>


    </xsl:template>

</xsl:stylesheet>
