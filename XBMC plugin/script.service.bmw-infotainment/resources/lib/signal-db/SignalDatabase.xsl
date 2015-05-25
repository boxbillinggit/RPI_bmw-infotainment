<?xml version="1.0"?>

<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="/">

<html>
<head>
	<title>IBUS signal database</title>

	<link rel="icon" type="image/png" href="img/favicon-16px.png" sizes="16x16"/>
	<link rel="icon" type="image/png" href="img/favicon-32px.png" sizes="32x32"/>
	<link rel="icon" type="image/png" href="img/favicon-64px.png" sizes="64x64"/>	
	
	<!-- load jQuery and JsTree  -->
	<link rel="stylesheet" href="js/jstree-dist/themes/default/style.min.css" />
	<script type="text/javascript" src="js/jquery-1.11.3.min.js"></script>
	<script type="text/javascript" src="js/jstree-dist/jstree.min.js"></script>
	<script>

		$(function() {
	
			$('.tree').jstree();
			
		});
		
	</script>
	
	<style type="text/css">
	
	body {
		font-family: arial;
	}
	
	.pdu {
		width: 800px;
		
	}
	
	.pdu #length {
		text-align: center;
		font-style: italic;
		border-bottom: 3px dotted blue
	}
	
	.pdu td {
		padding: 10px;
		vertical-align: top;
		padding: 10px;
	}
	
	.settings {
		background: #AEC3FF;
		
	}
	
	</style>
	
</head>
<body>
	
	<h1>SignalDatabase for BMW IBUS</h1>
	
	
	<h2>Image reference</h2>
	<img src="img/board-monitor.jpg" width="600px" />
	
	<h2>IBUS settings</h2>
	<table>
	
	<th>
		<td>Setting</td><td>Value</td>
	</th>
	
	<xsl:for-each select="IBUS/COM-settings/*">
	<tr class="settings">
		<td><xsl:value-of select="name()"/></td><td><xsl:value-of select="."/></td>
	</tr>
	 </xsl:for-each>
	
	</table>

	
	<h2>IBUS frame</h2>
	<table class="pdu">
	
	<tr>
		<td colspan="2"></td>
		<td colspan="3" id="length">Length</td>
	</tr>
	
	<tr style="background: #AEC3FF;">
		<td>
			<xsl:call-template name="device-codes">
				<xsl:with-param name="title">Source ID</xsl:with-param>
			</xsl:call-template>
		</td>
		
		<td><i>Length</i></td>
		
		<td>
			<xsl:call-template name="device-codes">
				<xsl:with-param name="title">Destination ID</xsl:with-param>
			</xsl:call-template>
		</td>
		
		<td>
			<!-- js tree -->
			<div class="tree">
				<ul>
					<li>Data
						<ul>
							<li>Operations
								<ul>
									<xsl:for-each select="IBUS/MESSAGE/DATA/CATEGORY[@type='operations']/*">
									<li><xsl:value-of select="@val"/> - <xsl:value-of select="."/>
										<!-- loop through all categories -->


									</li>
									</xsl:for-each>
								</ul>
							</li>
						</ul>

					</li>
				</ul>
			</div>
		</td>
		
		<td><i>Checksum</i></td>
	</tr>
	
	</table>
	
	<h2>Explore</h2>

	
</body>
</html>

</xsl:template>

<!-- template for device codes -->
<xsl:template name="device-codes">
	<xsl:param name="title" />

	<!-- 
		js tree 
		ref: http://www.jstree.com/docs/interaction/
	-->
	
	<div class="tree">
		<ul>
			<li><xsl:value-of select="$title" />
				<ul>
					<xsl:for-each select="IBUS/MESSAGE/DEVICES/*">
					<li><xsl:value-of select="@val"/> - <xsl:value-of select="."/></li>
					</xsl:for-each>
				</ul>
			</li>
		</ul>
	</div>
</xsl:template>


</xsl:stylesheet>