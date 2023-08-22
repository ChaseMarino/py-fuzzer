from os import link
import mechanicalsoup
import argparse
import time
# Connect to our course website

browser = mechanicalsoup.StatefulBrowser(user_agent='MechanicalSoup')

#browser.
# Find all links using the CSS selector
parser = argparse.ArgumentParser(description='fuzz [discover | test] url OPTIONS')
parser.add_argument('discover', nargs='?', help='Output a comprehensive, human-readable list of all discovered inputs to the system. Techniques include both crawling and guessing.')
parser.add_argument('test', nargs='?', help='Discover all inputs, then attempt a list of exploit vectors on those inputs. Report anomalies that could be vulnerabilities.')
#universal
parser.add_argument('--custom-auth', type=str, required=False, help='Signal that the fuzzer should use hard-coded authentication for a specific application (e.g. dvwa).')
#discover // universal 
parser.add_argument('--common-words', type=str, required=False, help='Newline-delimited file of common words to be used in page guessing. Required.')
parser.add_argument('--extensions', type=str, required=False, help='Newline-delimited file of path extensions, e.g. ".php". Optional. Defaults to ".php" and the empty string if not specified')
#test options
parser.add_argument('--vectors', type=int, required=False, help='Newline-delimited file of common exploits to vulnerabilities. Required.')
parser.add_argument('--sanitized-chars', type=int, required=False, help='Newline-delimited file of characters that should be sanitized from inputs. Defaults to just < and >')
parser.add_argument('--sensitive', type=int, required=False, help='Newline-delimited file data that should never be leaked. It\'s assumed that this data is in the application\'s database (e.g. test data), but is not reported in any response. Required.')
parser.add_argument('--slow', type=int, required=False, help='Number of milliseconds considered when a response is considered "slow". Optional. Default is 500 milliseconds')
args = vars(parser.parse_args())

def discover(args):
    #initial login
    if (args['custom_auth'] == 'None'):
        print('custom_auth option required with test command')
        return
    if (args['custom_auth'] == 'dvwa'):
        #reset database
        url = args['test']

        if (args['common_words'] != None):
            validUrlsFound = ''
            commonWordsFile = open(args['common_words'], "r")
            for word in commonWordsFile:
                currUrl = args['test'] + word.strip()
                #print(args)
                if (args['extensions'] != None):

                    commonExtensionsFile = open(args['extensions'], "r")
                    for ext in commonExtensionsFile:
                        currUrl = args['test'] + word.strip() + ext.strip()
                        if (browser.open(currUrl).status_code != 404):
                            validUrlsFound += currUrl + '\n'

                else:
                    currUrl += '.php'
                    if (browser.open(currUrl).status_code != 404):
                        validUrlsFound += currUrl + '\n'

            #remove logout.php
            print(validUrlsFound)
        visitedLinkList = []
        discoveredLinkList = []


        url = args['test'] + 'setup.php'
        browser.open(url)
        browser.select_form()
        browser.submit_selected()
        #login
        url = args['test']
        browser.open(url)
        browser.select_form()
        browser["username"] = "admin"
        browser["password"] = "password"
        browser.submit_selected()

        #change security
        url = args['test'] + 'security.php'
        browser.open(url)
        browser.select_form()
        browser["security"] = "low"
        browser.submit_selected()
        #return to index and print
        url = args['test'] + 'index.php'
        browser.open(url)
        print("\n\nHome Page Contents post login")
        print(browser.page)
        browserL = browser.links()
        formList = []
        for link in browserL:
            discoveredLinkList.append(str(link).split('\"')[1])
            
        visitedLinkList.append(browser.url)

        for link in discoveredLinkList:
            #sprint(link)
            if (link in visitedLinkList or any(invalidChar in ['http', ':', 'logout'] for invalidChar in link)):
                discoveredLinkList.remove(link)
            else:
                if ('logout' not in link):
                    try:
                        browser.open(args['test'] + link)
                        browserL = browser.links()
                        #formList.append("\n Page: " + args['test'] + link + "\n Forms: " + browser.page.find_all('form'))
                        for x in browser.page.find_all("input"):
                            for y in str(x).split():
                                if ('name=\"' in y):
                                    formList.append("Page: " + args['test'] + link + "Forms input name: " + y)

                    except:
                        pass

                    for link2 in browserL:
                        #print(link2)
                        if (str(link2).split('\"')[1] not in discoveredLinkList):   
                            discoveredLinkList.append(str(link2).split('\"')[1])
                    visitedLinkList.append(link)
                    discoveredLinkList.remove(link)
        print("\n\n Inputs found")
        print(formList)
        print("\n\n Links Crawled")
        print(visitedLinkList)




def test(args):
    return 1


if (args['discover'] == 'discover'):
    discover(args)
elif (args['test'] == 'test'):
    test(args)

