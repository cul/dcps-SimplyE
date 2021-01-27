<?xml version="1.0" encoding="UTF-8"?>
<!-- Stylesheet to convert ONIX 2.1 to ONIX 3, for ingest into SimplyE. Source and result use "reference" tags; to convert to short tags, use "switch-onix-3.0-tagnames-2.0.xsl. See Basecamp thread. -->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns="http://ns.editeur.org/onix/3.0/reference"
    exclude-result-prefixes="xs" 
    version="2.0">
    

    
    <xsl:output
        method="xml"
        omit-xml-declaration="no"
        standalone="yes"
        doctype-system="ONIX_BookProduct_DTDs+codes_Issue_51/ONIX_BookProduct_3.0_reference.dtd"
        indent="yes"
        encoding="UTF-8"
        />

    
    <xsl:template match="ONIXMessage">
        <ONIXMessage release="3.0">
        <xsl:apply-templates select="Header"/>
        <xsl:apply-templates select="Product"/>
      </ONIXMessage>
    </xsl:template>
    
    
    <!-- Import lookup to obtain bibids from isbn. See SET-36.   -->
    <xsl:variable name="isbn_lookup">
        <xsl:copy-of select="document('jhu_isbn_lookup.xml')"/>
    </xsl:variable>
    
    <xsl:template match="Header">
        <Header>
            <Sender>
                <SenderName><xsl:value-of select="FromCompany"/></SenderName>
                <ContactName><xsl:value-of select="FromPerson"/></ContactName>
                <EmailAddress><xsl:value-of select="FromEmail"/></EmailAddress>
            </Sender>

            <MessageNumber>231</MessageNumber>
            <SentDateTime>20200325T1115-0400</SentDateTime>
            <MessageNote>Sample message</MessageNote>
        </Header>
    </xsl:template>
    
    
    <xsl:template match="Product">
        <xsl:variable name="isbn">
            <xsl:value-of select="RecordReference"/>
        </xsl:variable>
        
        <Product>
           
            <xsl:apply-templates select="RecordReference" mode="copy-no-namespaces"/>
            <xsl:apply-templates select="NotificationType" mode="copy-no-namespaces"/>
            <xsl:apply-templates select="ProductIdentifier" mode="copy-no-namespaces"/>

            
            <DescriptiveDetail>
                <ProductComposition>00</ProductComposition>
                <ProductForm>EA</ProductForm>
                
<!--             Type: EPUB or PDF?   -->
                <xsl:choose>
                    <xsl:when test="EpubType = '002'">
                        <!--			PDF --> <ProductFormDetail>E107</ProductFormDetail>
                    </xsl:when>
                    <xsl:when test="EpubType = '029'">
                        <!--			EPUB -->  <ProductFormDetail>E101</ProductFormDetail>
                    </xsl:when>
                </xsl:choose>
              
                
                
                <!--	leave out classification, collection		-->
                
                <TitleDetail>
                    <TitleType>01</TitleType>
                    <TitleElement>
                        <TitleElementLevel>01</TitleElementLevel>
 
                        <TitleText><xsl:value-of select="Title/TitleText"/></TitleText>
                        <xsl:apply-templates select="Title/Subtitle" mode="copy-no-namespaces"/>
                       
                    </TitleElement>
                </TitleDetail>
                
                
<!--                Contributors -->
               <xsl:for-each select="Contributor">
                   <xsl:apply-templates select="." mode="copy-no-namespaces"/>
               </xsl:for-each>
      		
                <xsl:apply-templates select="ContributorStatement" mode="copy-no-namespaces"/>
      		
                <xsl:apply-templates select="Language" mode="copy-no-namespaces"/>
    
    
                <!--			page count-->
                <Extent>
                    <ExtentType>07</ExtentType>
                    <ExtentValue><xsl:value-of select="NumberOfPages"/></ExtentValue>
                    <ExtentUnit>03</ExtentUnit>
                </Extent>
                
                
<!--            SUBJECTS    -->
  
                <xsl:for-each select="Subject">
                    <xsl:apply-templates select="." mode="copy-no-namespaces"/>
                </xsl:for-each>
  
                
                <!-- skip audience-->
            </DescriptiveDetail>
    
            <CollateralDetail>
<!--            Description text    -->
                <TextContent>
                    <TextType>03</TextType>
                    <ContentAudience>00</ContentAudience>
                    <Text>
                        <!-- Do any cleanup to description text, and add catalog link with BIBID. -->
                        <xsl:apply-templates select="OtherText/Text">
                        <xsl:with-param name="bibid">
                            <xsl:value-of select="$isbn_lookup/lookup/record[isbn=$isbn]/bibid"/>
                        </xsl:with-param>
                    </xsl:apply-templates>
                    </Text>
                </TextContent>
                
            </CollateralDetail>
 
            
            <!-- there is no Block 3 -->
            <PublishingDetail>
                <Imprint>
                    <ImprintName>Johns Hopkins University Press</ImprintName>
                </Imprint>
                <Publisher>
                    <PublishingRole>01</PublishingRole>
                    
                    <PublisherName>Johns Hopkins University Press</PublisherName>
                    <Website>
                        <WebsiteRole>01</WebsiteRole>
                        <WebsiteLink>http://jhupbooks.press.jhu.edu</WebsiteLink>
                    </Website>
                </Publisher>
                
                
            </PublishingDetail>
            
            
            
        </Product>
    </xsl:template>
    
    <xsl:template match="*" mode="copy-no-namespaces">
        <xsl:element name="{local-name()}">
            <xsl:copy-of select="@*"/>
            <xsl:apply-templates select="node()" mode="copy-no-namespaces"/>
        </xsl:element>
    </xsl:template>
    
    
    <!-- Process the book description, including adding link to CLIO -->
    <xsl:template match="OtherText/Text">
        <xsl:param name="bibid"/>
        <!-- Fix em dashes and other garbled characters -->
        <xsl:analyze-string select="." regex="(â€”|Ã¢â‚¬â€\?)">
            <xsl:matching-substring>—</xsl:matching-substring>
            <xsl:non-matching-substring>
                <xsl:analyze-string select="." regex="Ã©">
                    <xsl:matching-substring>é</xsl:matching-substring>
                    <xsl:non-matching-substring>
                        <xsl:analyze-string select="." regex="â€™">
                            <xsl:matching-substring>’</xsl:matching-substring>
                            <xsl:non-matching-substring><xsl:value-of select="."/></xsl:non-matching-substring>
                        </xsl:analyze-string>
                    </xsl:non-matching-substring>
                </xsl:analyze-string>
            </xsl:non-matching-substring>
        </xsl:analyze-string>
        
        <!-- if last <Text>, append the catalog link. -->
        <xsl:if test="not(ancestor::OtherText[following-sibling::OtherText])">
        <xsl:text> &lt;P&gt;&lt;a href="https://clio.columbia.edu/catalog/</xsl:text>
        <xsl:value-of select="$bibid"/>
        <xsl:text>"&gt;Go to catalog record in CLIO.&lt;/a&gt;&lt;/P&gt;</xsl:text>
        </xsl:if>
        
    </xsl:template>
    
</xsl:stylesheet>