A quick API i wrote up for aggregating data from various music sites. 
EDIT 9/5/12: Looks like Billboard integration is broken now, and the lastFM public API is shut down. Pls don't steal my lfm key.

Example output (without Billboard):

Results for Sweet Disposition by The Temper Trap

 Last.fm recommends:
Love Lost - The Temper Trap, 2009 (0.65)
Fader - The Temper Trap, 2009 (0.65)
There Goes The Fear - Doves, 2009 (0.55)
Tongue Tied - Grouplove, 2011 (0.74)
Cough Syrup - Young the Giant, 2010 (0.75)


Copy/Paste from assignment write-up:

Grooveshark/TinyShark: The TinyShark API, which is smaller and more public than the official grooveshark api to which I have yet to be granted an access key (applied a week ago), is basically just an imput manager. Of the systems I could find, it was the only one that would take a string that could be an artist name or an album name or a track name or any combination of the three and would try to guess which specific tracks I was interested in. This seemed useful, as it effectively outsources nearly all input management.
Billboard: The rather unpredictable Billboard API allows for specific searches on the Billboard chart database, allowing you to look up whether a given artist or track was ever on their top 100 (or some absurd number of other "top" lists they have) over a specified span of time. The only problem with this tool is that it has a tendency to default in cases where other systems would simply return nothing, showing the current top tracks, which is made worse by it's dependency on knowing both track name, artist name, and the time span in which the track or artist might have made the charts; there is no real open ended search tool. This means that some after the fact parsing will be necessary to make sure it isn't sending back completely wrong data. All that said, when it does work the data about if/when an artist made the top charts and how long that stayed up there could lead to some interesting analysis, perhaps looking into large scare trends over time, as Billboard is the only tool that has any sort of temporal element to its data.
Spotify: Similar in use to TinyShark, the Spotify API lets you enter in a track name, artist name, or album name, and throws back information about that object. It does require a little more structure than TinyShark, as it has separate methods for those three things while TinyShark has only one, but it would be possible to string the 3 together with some input parsing and assume the returned element with the most data is the correct one. Spotify also gives more specific information such as release date (necessary for billboard searches) and a popularity value between 0 and 1 that reflects the relative activity a given album, artist, or track has been receiving recently. An idea for an interesting thing to look up would be the ways in which single hits change an artists popularity or album popularity, even if other songs by the artist are relatively unpopular, or to see what sort of distribution forms around the non-hit work of artists with tracks high on Billboard's charts.
last.fm: The last.fm API is the only one with any sort of open "similar tracks/artists" feature, and seems to have a pretty good one. The API lets you search for similar tracks to a query, similar tags to a tag on a track/artist/album,  and similar artists with a "match" variable indicating the average overlap of user interest in the two artists, a feature sadly not available for single tracks or albums. It also has something akin to Spotify's popularity metric as each track has data for both the total number of logged plays and the number of "listeners," or users who have that track on one or more playlists. In honestly, after working with the other APIs I felt like I might have been better off only interacting with this one, but I suppose there are different sorts of data to be gained from the other systems.

