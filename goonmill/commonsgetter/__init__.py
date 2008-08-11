"""
A utility I used to scrape the wikimedia commons for search results and then
images relating to monsters in the monster list.

TODO - should be reimplemented.

A proper implementation should do this:


============================
commonsgetter monster images
============================

0. srd database
1. prep list by dropping everything after a comma (i.e. ".., Ancient")
1.5 prep list by dropping certain prefixes (i.e. "Dire ..") - create this
list of prefixes
- devastation
- greater
- legendary
- air
- fire
- average
- behemoth
- dire
- dread
- earth
- elder
- water
- monstrous
- juvenile
- giant
- minor
- *-headed


2. for remaining unique names, query wikiwix with each name as a search
and save page1 of results as json into mediawiki.js
3. Read out mediawiki.js and visit each html page
4. Use getimageurls.py to find any img src containing 'commons/' and write
it, along with monster, to tab-delim file mediawiki.urls
5. Use getimages.py to download from mediawiki.urls to directories named
for the monster
5.5 skip any image already seen and any monster with no images 
6. manually sift all directories for images that are obviously useless and
discard. discard empty directories.  might want to make 2 passes at this.
7. locate and document license on all images
- http://en.wikipedia.org/wiki/GNU_Free_Documentation_License
- http://creativecommons.org/licenses/by-sa/2.0/
- http://en.wikipedia.org/wiki/Public_domain
8. in remaining images, process in gimp.. extract from background and add
paint strokes unless already stylized.
9. convert to color palette
"""
