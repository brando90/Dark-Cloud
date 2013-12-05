# Include the Dropbox SDK
import dropbox

# Get your app key and secret from the Dropbox developer website
app_key = 'INSERT_APP_KEY'
app_secret = 'INSERT_APP_SECRET'

flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)

#Returns the URL for a page on Dropbox’s website. This page will let the user “approve” your app,
#which gives your app permission to access the user’s Dropbox account. 
#Tell the user to visit this URL and approve your app.

authorize_url = flow.start()