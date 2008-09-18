LEXICO_Globals = new Object();
LEXICO_Globals.HTML = new Object();
LEXICO_Globals.HTML.anchors = document.getElementsByTagName('a');
LEXICO_Globals.TabTargetLinks = new Object();
LEXICO_Globals.TabTargetLinks.searchId = '';
LEXICO_Globals.SafeOnload = new Array();

// Browser Detection
isMac = (navigator.appVersion.indexOf("Mac")!=-1) ? true : false;
NS4 = (document.layers) ? true : false;
IEmac = ((document.all)&&(isMac)) ? true : false;
IE4plus = (document.all) ? true : false;
IE4 = ((document.all)&&(navigator.appVersion.indexOf("MSIE 4.")!=-1)) ? true : false;
IE5 = ((document.all)&&(navigator.appVersion.indexOf("MSIE 5.")!=-1)) ? true : false;
IE6 = ((document.all)&&(navigator.appVersion.indexOf("MSIE 6.")!=-1)) ? true : false;
IE7 = ((document.all)&&(navigator.appVersion.indexOf("MSIE 7.")!=-1)) ? true : false;
ver4 = (NS4 || IE4plus) ? true : false;
NS6 = (!document.layers) && (navigator.userAgent.indexOf('Netscape')!=-1)?true:false;
function LEXCIO_GetEventSource(e)
	{
	if ( e && e.target )
		{
		// HACK for NN 6 because NN 6 trigger event from text node 
		var event = e && e.target;
		while (event && event.nodeType == 3)
			event = event.parentNode

		return (event);
		}
		
	if (window && window.event && window.event.srcElement)
		return (window && window.event && window.event.srcElement);
	
	return false;		
	}

// =================================================================
// BEGIN: Add Tab Target Links 
// =================================================================
function AddTabTargetLinks()
	{
	if (AddTabTargetLinks.arguments.length != 1) return false;
	var anchors = LEXICO_Globals.HTML.anchors;
	
	LEXICO_Globals.TabTargetLinks.searchId = AddTabTargetLinks.arguments[0];

	for (var anchorIndex=0; anchorIndex < anchors.length; anchorIndex++) 
		{
		var currentAnchor = anchors[anchorIndex];
	    	var relInformation = currentAnchor.getAttribute("rel");

		if (typeof(clicked) == "undefined") clicked = false;

		// Don't set up this event if all three cases aren't true
		if (relInformation == 'tab' && document.getElementById && LEXICO_Globals.TabTargetLinks.searchId != '')
			{
			currentAnchor.onmouseup = TabTargetLinks;
			currentAnchor.onmouseover = LEXICO_SetStatusMessage;
			currentAnchor.onmouseout = LEXICO_ClearStatusMessage;
			}
			
		}
	}
function TabTargetLinks(e) {
	e = (e) ? e : ((window.event) ? window.event : "")
	if (e) 
		{
		var eventsource = LEXCIO_GetEventSource(e);		
		// Make sure you aren't using a text node
		while (eventsource.nodeType == 3) 
			eventsource = eventsource.parentNode;

		if (typeof(redirectURL) != "undefined") eventsource.href = redirectURL;
		clicked = true;

		}
}
function GetSearchBoxInformation(){
	var currentElement = null;
	currentElement = document.getElementById(LEXICO_Globals.TabTargetLinks.searchId);

	var returnString = "";
	if (currentElement && currentElement.nodeName.toLowerCase() == "input" && currentElement.value != "") returnString = currentElement.value;
	 	
 	return encodeURIComponent(returnString);
}	
function LEXICO_SetStatusMessage(e){
	e = (e) ? e : ((window.event) ? window.event : "")
	if (typeof(clicked) == "undefined") return;
	if (e) 
		{
		var eventsource = LEXCIO_GetEventSource(e);				
		var clickedTabHREF = new String(eventsource.href)
		var searchTerm = GetSearchBoxInformation();
		var urlArray = new String(window.location);
		var currentURL = new String(window.location);
		if (searchTerm != "")
			{
			if (clickedTabHREF.search(LEXICO_Globals.SiteInfo.dictionaryURL) == 0)
				redirectURL = LEXICO_Globals.SiteInfo.dictionaryURL + '/browse/' + searchTerm; 
			else if (clickedTabHREF.search(LEXICO_Globals.SiteInfo.thesaurusURL) == 0)
				redirectURL = LEXICO_Globals.SiteInfo.thesaurusURL + '/browse/' + searchTerm;
			else if ((clickedTabHREF.indexOf('db=web') != -1) || (clickedTabHREF.search(LEXICO_Globals.SiteInfo.thewebURL) == 0))
				redirectURL = LEXICO_Globals.SiteInfo.referenceURL + '/search?q=' + searchTerm + '&db=web';
			else if (clickedTabHREF.search(LEXICO_Globals.SiteInfo.allURL) == 0)
				redirectURL = LEXICO_Globals.SiteInfo.referenceURL + '/browse/all/' + searchTerm;
			else if (clickedTabHREF.search(LEXICO_Globals.SiteInfo.referenceURL) == 0) 
				redirectURL = LEXICO_Globals.SiteInfo.referenceURL + "/search?q=" + searchTerm;
		
			window.status = redirectURL;
			}
		else
			{
			if (clickedTabHREF.search(LEXICO_Globals.SiteInfo.dictionaryURL) == 0)
				redirectURL = LEXICO_Globals.SiteInfo.dictionaryURL + '/'; 
			else if (clickedTabHREF.search(LEXICO_Globals.SiteInfo.thesaurusURL) == 0)
				redirectURL = LEXICO_Globals.SiteInfo.thesaurusURL + '/';
			else if ((clickedTabHREF.indexOf('db=web') != -1) || (clickedTabHREF.search(LEXICO_Globals.SiteInfo.thewebURL) == 0))
				redirectURL = LEXICO_Globals.SiteInfo.referenceURL + '/?db=web';
			else if (clickedTabHREF.search(LEXICO_Globals.SiteInfo.allURL) == 0)
				redirectURL = LEXICO_Globals.SiteInfo.referenceURL + '/browse/all/';
			else if (clickedTabHREF.search(LEXICO_Globals.SiteInfo.referenceURL) == 0) 
				redirectURL = LEXICO_Globals.SiteInfo.referenceURL + '/';
		
			window.status = redirectURL;
			}
		return true;
		}
}
function LEXICO_ClearStatusMessage(e){
	e = (e) ? e : ((window.event) ? window.event : "")
	if (typeof(clicked) == "undefined") return;
	if (e) 
		{
			window.status = "";
		}

	return true;
}
// =================================================================
// END: Add Tab Target Links 
// =================================================================

// =================================================================
// BEGIN: SafeOnload
// =================================================================

// Body onload utility (supports multiple onload functions)
var gSafeOnload = new Array();
function SafeAddOnload(f){
	if (IEmac && IE4)  // IE 4.5 blows out on testing window.onload
		{
		window.onload = SafeOnload;
		LEXICO_Globals.SafeOnload[LEXICO_Globals.SafeOnload.length] = f;
		}
	else if  (window.onload)
		{
		if (window.onload != SafeOnload)
			{
			LEXICO_Globals.SafeOnload[0] = window.onload;
			window.onload = SafeOnload;
			}		
		LEXICO_Globals.SafeOnload[LEXICO_Globals.SafeOnload.length] = f;
		}
	else
		window.onload = f;
}
function SafeOnload(){
	for (var i=0;i<LEXICO_Globals.SafeOnload.length;i++)
		LEXICO_Globals.SafeOnload[i]();
}
// =================================================================
// END: SafeOnload
// =================================================================


// =================================================================
// BEGIN: DetermineRedirectURL
// =================================================================
function DetermineRedirectURL(queryString){
	queryString = encodeURIComponent(queryString);
	var returnURL;

	if( LEXICO_Globals.SiteInfo.currentSite == "thesaurus")
		returnURL = LEXICO_Globals.SiteInfo.thesaurusURL + "/browse/" + queryString;
	else if( LEXICO_Globals.SiteInfo.currentSite == "dictionary")
		returnURL = LEXICO_Globals.SiteInfo.dictionaryURL + "/browse/" + queryString;
	else if ( LEXICO_Globals.SiteInfo.currentSite == "reference")
		returnURL = LEXICO_Globals.SiteInfo.referenceURL + "/search?q=" + queryString;
	else if ( LEXICO_Globals.SiteInfo.currentSite == "theweb")
		returnURL = LEXICO_Globals.SiteInfo.referenceURL + "/search?q=" + queryString + '&db=web';
	else if ( LEXICO_Globals.SiteInfo.currentSite == "all")
		returnURL = LEXICO_Globals.SiteInfo.referenceURL + "/browse/all/" + queryString;

	return returnURL;
}
// =================================================================
// END: DetermineRedirectURL
// =================================================================

// =================================================================
// BEGIN: HideAppropiateBookmarklets
// =================================================================

function HideAppropiateBookmarklets(){
	if (HideAppropiateBookmarklets.arguments.length != 1) return;

	var currentElement = document.getElementById(HideAppropiateBookmarklets.arguments[0]);
	if (currentElement) currentElement.style.display = "none";		
}
function DetermineVisableBookmarklets()	{
	if (document.getElementById)
		{
		var agent = navigator.userAgent.toLowerCase()
		var appVersion = navigator.appVersion.toLowerCase();
	
		var isMac = (agent.indexOf("mac")!=-1);
		var iePos  = appVersion.indexOf('msie');
		if (iePos !=-1)	
			{
		   	if(isMac) 
		   		{
			   	var iePos = agent.indexOf('msie');
		   		}
			}	
		
		var isOpera = (agent.indexOf("opera") != -1);
		var isSafari = ((agent.indexOf('safari')!=-1)&&(agent.indexOf('mac')!=-1))?true:false;
	
		var isKonq = false;
		var kqPos   = agent.indexOf('konqueror');
		if (kqPos !=-1) isKonq  = true;
	
		var isKhtml  = (isSafari || isKonq);
		var isGecko = ((!isKhtml)&&(navigator.product)&&(navigator.product.toLowerCase()=="gecko"))?true:false;	
	
		var isFirebird = ((agent.indexOf('mozilla/5')!=-1) && (agent.indexOf('spoofer')==-1) &&
					 (agent.indexOf('compatible')==-1) && (agent.indexOf('opera')==-1)  &&
					 (agent.indexOf('webtv')==-1) && (agent.indexOf('hotjava')==-1)     &&
					 (isGecko) && (navigator.vendor=="Firebird"));
		var isFirefox = ((agent.indexOf('mozilla/5')!=-1) && (agent.indexOf('spoofer')==-1) &&
					 (agent.indexOf('compatible')==-1) && (agent.indexOf('opera')==-1)  &&
					 (agent.indexOf('webtv')==-1) && (agent.indexOf('hotjava')==-1)     &&
					 (isGecko) && ((navigator.vendor=="Firefox")||(agent.indexOf('firefox')!=-1)));
		var isMozzilla  = ((agent.indexOf('mozilla/5')!=-1) && (agent.indexOf('spoofer')==-1) &&
						(agent.indexOf('compatible')==-1) && (agent.indexOf('opera')==-1)  &&
						(agent.indexOf('webtv')==-1) && (agent.indexOf('hotjava')==-1)     &&
						(isGecko) && (!isFirebird) && (!isFirefox) &&
						((navigator.vendor=="")||(navigator.vendor=="Mozilla")||(navigator.vendor=="Debian")));
						
		var isNav  = ((agent.indexOf('mozilla')!=-1) && (agent.indexOf('spoofer')==-1)
					&& (agent.indexOf('compatible') == -1) && (agent.indexOf('opera')==-1)
					&& (agent.indexOf('webtv')==-1) && (agent.indexOf('hotjava')==-1)
					&& (!isKhtml) && (!(isMozzilla)) && (!isFirebird) && (!isFirefox));
	
		var isInternetExplorer   = ((iePos!=-1) && (!isOpera) && (!isKhtml));
		var displayAllBrowsers = true;
	
		if (!isInternetExplorer) HideAppropiateBookmarklets("ieblock");
		
		if (!isNav) HideAppropiateBookmarklets("netscapeblock");
		
		if (!isFirebird && !isMozzilla && !isFirefox) HideAppropiateBookmarklets("firefoxblock");

		if (!isOpera) HideAppropiateBookmarklets("operablock");
		
		if (!isSafari) HideAppropiateBookmarklets("saphariblock");

		
		var currentElement = document.getElementById("allbrowsersblock");
		if (currentElement) currentElement.style.display = "block";		
		}	
	else
		window.location = "allbookmarklets.html"
}
// =================================================================
// END: HideAppropiateBookmarklets
// =================================================================
function LEXICO_GetCurrentFileName(){
	var URL = unescape( window.location.pathname );
	var start = URL.lastIndexOf( "/" ) + 1;
	var end = ( URL.indexOf( "?" ) > 0 ) ? URL.indexOf( "?" ) : URL.length;
	return( URL.substring( start, end ) );
}
function LEXICO_GetCurrentFilePath(){
	var URL = unescape( window.location.pathname );
	var start = URL.lastIndexOf( "/" );
	return( URL.substring( 0, start ) );
}
function LEXICO_GetCurrentDirectory(){
	var filePath = LEXICO_GetCurrentFilePath();
	var directories = filePath.split("/");	
	currentDirectory = "";
	for (index = 0; index < directories.length; index++)
		{
		currentDirectory += directories[index]
		if (index != directories.length - 1)
			currentDirectory += "/"
		}
	return currentDirectory;
}	
// =================================================================
// BEGIN: Common Scripts needed throughout the site.
// =================================================================
function onMouseOver_Status (s) {
	window.status=s;
	return true;
}
function onMouseOut_Status () {
	window.status='';
	return true;
}
function ShowHide_cite (d) {
	tableObject = document.getElementById('citetable');
	if (!(tableObject && document.getElementsByTagName)) return true;
		tableDivs = tableObject.getElementsByTagName("div");
	if (!tableDivs) return true;
	
	for (index = 0; index < tableDivs.length; index++)
		{
		tableDivs[index].style.display = "none";
		}

	if ( document.getElementById(d).style.display == "none" ) {

		document.getElementById(d).style.display = "";
	}
	else {
		document.getElementById(d).style.display = "none";
	}
	
	return false;
}
function ShowHide_save (d) {
	tableObject = document.getElementById('citetable');
	if (!(tableObject && document.getElementsByTagName)) return true;
		tableDivs = tableObject.getElementsByTagName("div");
	if (!tableDivs) return true;
	
	for (index = 0; index < tableDivs.length; index++)
		{
		tableDivs[index].style.display = "none";
		}

	if ( document.getElementById(d).style.display == "none" ) {

		document.getElementById(d).style.display = "";
	}
	else {
		document.getElementById(d).style.display = "none";
	}
	
	return false;
}
function ShowHide_share (d) {
	tableObject = document.getElementById('citetable');
	if (!(tableObject && document.getElementsByTagName)) return true;
		tableDivs = tableObject.getElementsByTagName("div");
	if (!tableDivs) return true;
	
	for (index = 0; index < tableDivs.length; index++)
		{
		tableDivs[index].style.display = "none";
		}

	if ( document.getElementById(d).style.display == "none" ) {

		document.getElementById(d).style.display = "";
	}
	else {
		document.getElementById(d).style.display = "none";
	}
	
	return false;
}
function ShowHide_toolbardownload (d) {
	tableObject = document.getElementById('downloadtable');
	if (!(tableObject && document.getElementsByTagName)) return true;
		tableDivs = tableObject.getElementsByTagName("div");
	if (!tableDivs) return true;
	
	for (index = 0; index < tableDivs.length; index++)
		{
		tableDivs[index].style.display = "none";
		}

	if ( document.getElementById(d).style.display == "none" ) {

		document.getElementById(d).style.display = "";
	}
	else {
		document.getElementById(d).style.display = "none";
	}
	
	return false;
}
// =================================================================
// END: Common Scripts needed throughout the site.
// =================================================================		

// =================================================================
// Please don't touch this section
// =================================================================
function init()	{
	AddTabTargetLinks('search-terms');
	if (LEXICO_GetCurrentDirectory() == "/tools" && LEXICO_GetCurrentFileName() == "bookmarklets.html") DetermineVisableBookmarklets();
}
window.onload = init;
