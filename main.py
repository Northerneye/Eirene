from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivymd.uix.button import MDFloatingActionButtonSpeedDial, MDIconButton, MDFlatButton, MDRaisedButton, MDFillRoundFlatIconButton
from kivymd.uix.dialog import MDDialog

from kivymd.uix.textfield.textfield import MDTextField
from kivy.properties import StringProperty, ObjectProperty

from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.fitimage import FitImage

from kivymd.uix.navigationdrawer import (
    MDNavigationLayout,
    MDNavigationDrawer,
    MDNavigationDrawerMenu,
    MDNavigationDrawerHeader,
    MDNavigationDrawerLabel,
    MDNavigationDrawerDivider,
    MDNavigationDrawerItem,
)
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import Snackbar

from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.toolbar import MDTopAppBar

from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.gridlayout import MDGridLayout

from kivymd.uix.imagelist.imagelist import MDSmartTile
from kivymd.uix.swiper.swiper import MDSwiper, MDSwiperItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.scrollview import MDScrollView
import socket

import threading
import json
import time

import TrueDemocracyBlockchain as tdm

global blockchain 
blockchain = tdm.Blockchain()

global proposed_laws_short
proposed_laws_short = []

global viewing_proposed_laws_short
viewing_proposed_laws_short = []

global proposed_laws_legal
proposed_laws_legal = []

global viewing_proposed_laws_legal
viewing_proposed_laws_legal = []

global proposed_laws_hash
proposed_laws_hash = []

global viewing_proposed_laws_hash
viewing_proposed_laws_hash = []

global proposed_laws_pcoin
proposed_laws_pcoin = []

global viewing_proposed_laws_pcoin
viewing_proposed_laws_pcoin = []

global established_laws_short
established_laws_short = []

global established_laws_legal
established_laws_legal = []

global viewing_established_laws_short
viewing_established_laws_short = []

global viewing_established_laws_legal
viewing_established_laws_legal = []

global server_started
server_started = False

def update_proposed_laws():
    global blockchain
    global proposed_laws_short
    global proposed_laws_legal
    global proposed_laws_hash
    global proposed_laws_pcoin
    short, legal, pcoin = blockchain.get_proposed_laws_text()
    proposed_laws_short = [value for key, value in short.items()]
    proposed_laws_legal = [value for key, value in legal.items()]
    proposed_laws_hash = [key for key, value in short.items()]
    proposed_laws_pcoin = [value for key, value in pcoin.items()]
    return proposed_laws_short, proposed_laws_legal, proposed_laws_hash

def update_established_laws():
    global blockchain
    global established_laws_short
    global established_laws_legal
    short, legal = blockchain.get_passed_laws_text()
    established_laws_short = [value for key, value in short.items()]
    established_laws_legal = [value for key, value in legal.items()]
    return established_laws_short, established_laws_legal

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

class BaseNavigationDrawerItem(MDNavigationDrawerItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.radius = 24
        self.text_color = "#4a4939"
        self.icon_color = "#4a4939"
        self.focus_color = "#e7e4c0"


class DrawerLabelItem(BaseNavigationDrawerItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.focus_behavior = False
        self._no_ripple_effect = True
        self.selected_color = "#4a4939"

class Eirene(MDApp):
    dialog = None

    def build(self):
        global proposed_laws_short
        global viewing_proposed_laws_short
        global proposed_laws_legal
        global viewing_proposed_laws_legal
        global proposed_laws_hash
        global viewing_proposed_laws_hash
        global proposed_laws_pcoin
        global viewing_proposed_laws_pcoin
        global established_laws_short
        global established_laws_legal
        global viewing_established_laws_short
        global viewing_established_laws_legal

        update_proposed_laws()
        viewing_proposed_laws_short = proposed_laws_short[:]
        viewing_proposed_laws_legal = proposed_laws_legal[:]
        viewing_proposed_laws_hash = proposed_laws_hash[:]
        viewing_proposed_laws_pcoin = proposed_laws_pcoin[:]
        update_established_laws()
        viewing_established_laws_short = established_laws_short[:]
        viewing_established_laws_legal = established_laws_legal[:]

        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Dark"

        self.screen_manager = MDScreenManager()
        
        self.refresh()
        
        self.navigation_drawer = MDNavigationDrawer(
            MDNavigationDrawerMenu(
                MDNavigationDrawerHeader(
                    title="Eirene",
                    title_color="#4a4939",
                    text="",
                    spacing="4dp",
                    padding=("12dp", 0, 0, "56dp"),
                ),
                MDNavigationDrawerLabel(
                    text="Home",
                ),
                BaseNavigationDrawerItem(
                    icon="home",
                    right_text="+99",
                    text_right_color="#4a4939",
                    text="Home",
                    ripple_color = "#c5bdd2",
                    selected_color = "#0c6c4d",
                    on_press = self.switch_screen
                ),
                MDNavigationDrawerDivider(),
                MDNavigationDrawerLabel(
                    text="Voting",
                ),
                BaseNavigationDrawerItem(
                    icon="ballot-outline",
                    right_text="+99",
                    text_right_color="#4a4939",
                    text="Current Vote",
                    ripple_color = "#c5bdd2",
                    selected_color = "#0c6c4d",
                    on_press = self.switch_screen
                ),
                MDNavigationDrawerDivider(),
                MDNavigationDrawerLabel(
                    text="CCoin",
                ),                                   
                BaseNavigationDrawerItem(
                    icon="cash",
                    text="CCoin Transaction",
                    ripple_color = "#c5bdd2",
                    selected_color = "#0c6c4d",
                    on_press = self.switch_screen
                ),
                MDNavigationDrawerDivider(),
                MDNavigationDrawerLabel(
                    text="Laws",
                ),
                BaseNavigationDrawerItem(
                    icon="gavel",
                    text="Search Established Laws",
                    ripple_color = "#c5bdd2",
                    selected_color = "#0c6c4d",
                    on_press = self.switch_screen
                ),
                BaseNavigationDrawerItem(
                    icon="scale-balance",
                    text="Search Proposed Laws",
                    ripple_color = "#c5bdd2",
                    selected_color = "#0c6c4d",
                    on_press = self.switch_screen
                ),
                BaseNavigationDrawerItem(
                    icon="lead-pencil",
                    text="Draft Laws",
                    ripple_color = "#c5bdd2",
                    selected_color = "#0c6c4d",
                    on_press = self.switch_screen
                ),
                MDNavigationDrawerDivider(),
                MDNavigationDrawerLabel(
                    text="Blockchain",
                ),
                BaseNavigationDrawerItem(
                    icon="human-greeting-proximity",
                    text="Manage Connections",
                    ripple_color = "#c5bdd2",
                    selected_color = "#0c6c4d",
                    on_press = self.switch_screen
                ),
            ),
            id="nav_drawer",
            radius=(0, 16, 16, 0),
        )
        
        self.navigation = MDNavigationLayout(self.screen_manager, self.navigation_drawer, id="navigation_layout")
        return self.navigation
        
    def Homepage(self):
        blockchain.save()
        myscreen = MDScreen(
            MDTopAppBar(
                title="Homepage",
                elevation=4,
                pos_hint={"top": 1},
                md_bg_color="#e7e4c0",
                specific_text_color="#4a4939",
                left_action_items=[
                    ['menu', lambda x: self.nav_drawer_open()]
                ],
            ),
            name="homepage"
        )

        pcoin_text = MDLabel(text="My PCoin: "+str(blockchain.get_pcoin_balance()), halign="center", pos_hint={"center_x":0.8, "center_y":0.8})
        myscreen.add_widget(pcoin_text)

        ccoin_text = MDLabel(text="My CCoin: "+str(blockchain.get_ccoin_balance()), halign="center", pos_hint={"center_x":0.2, "center_y":0.8})
        myscreen.add_widget(ccoin_text)

        current_vote_text = MDLabel(text="Current Vote:\n"+str(blockchain.get_current_law_text()[0]), font_style="H4", halign="center", pos_hint={"center_x":0.5, "center_y":0.5})
        myscreen.add_widget(current_vote_text)

        #mine_button = MDRaisedButton(text="Mine", pos_hint={"center_x": .3, "center_y": .2})
        #def mine(self, *args):
        #    blockchain.mine()
        #    blockchain.save()
        #    print(blockchain.get_chain())
        #    return Snackbar(
        #        text="Mined",
        #        snackbar_x="10dp",
        #        snackbar_y="10dp",
        #        size_hint_x=.3
        #    ).open()
        #mine_button.bind(on_release=mine)
        #myscreen.add_widget(mine_button)

        #save_button = MDRaisedButton(text="Save Blockchain", pos_hint={"center_x": .7, "center_y": .2})
        #def save(self, *args):
        #    blockchain.save()
        #    print(blockchain.get_chain())
        #    return Snackbar(
        #        text="Saved",
        #        snackbar_x="10dp",
        #        snackbar_y="10dp",
        #        size_hint_x=.3
        #    ).open()
        #save_button.bind(on_release=save)
        #myscreen.add_widget(save_button)

        return myscreen
    
    def Current_Vote_Page(self):
        myscreen = MDScreen(
            MDTopAppBar(
                title="Current Vote",
                elevation=4,
                pos_hint={"top": 1},
                md_bg_color="#e7e4c0",
                specific_text_color="#4a4939",
                left_action_items=[
                    ['menu', lambda x: self.nav_drawer_open()]
                ],
            ),
            name="current_vote"
        )

        current_law_short, current_law_legal, current_pcoin = blockchain.get_current_law_text()

        pcoin_text = MDLabel(text="pcoin: "+str(current_pcoin), halign="center", pos_hint={"center_x":0.85, "center_y":0.85})
        myscreen.add_widget(pcoin_text)
        
        short_text = MDLabel(text=current_law_short, size_hint_x=0.5, halign="center", valign="top", font_style="H4", pos_hint={"center_x":0.5, "center_y":0.8})
        myscreen.add_widget(short_text)

        law_text = MDLabel(text=current_law_legal, size_hint_x=0.5, halign="center", valign="top", font_style="H6", pos_hint={"center_x":0.5, "center_y":0.45})
        myscreen.add_widget(law_text)

        searchbar = MDTextField(icon_left="comment", pos_hint={"center_x":0.5, "center_y":0.1}, size_hint=[0.5,None])
        searchbar.bind(on_text_validate=self.search_established(searchbar, myscreen))
        myscreen.add_widget(searchbar)

        yes_comments_title = MDLabel(text="Yes-Comments", size_hint_x=0.25, theme_text_color="Custom", text_color=[0,1,0,1], halign="center", valign="top", font_style="H6", pos_hint={"left":1.0, "center_y":0.8})
        myscreen.add_widget(yes_comments_title)

        yes_comments = MDLabel(text="\n".join(blockchain.get_yes_comments()), size_hint_x=0.25, theme_text_color="Custom", text_color=[1,1,1,1], halign="center", valign="top", font_style="H6", pos_hint={"left":1.0, "center_y":0.5})
        myscreen.add_widget(yes_comments)

        no_comments_title = MDLabel(text="No-Comments", size_hint_x=0.25, theme_text_color="Custom", text_color=[1,0,0,1], halign="center", valign="top", font_style="H6", pos_hint={"right":1.0, "center_y":0.8})
        myscreen.add_widget(no_comments_title)

        no_comments = MDLabel(text="\n".join(blockchain.get_no_comments()), size_hint_x=0.25, theme_text_color="Custom", text_color=[1,1,1,1], halign="center", valign="top", font_style="H6", pos_hint={"right":1.0, "center_y":0.5})
        myscreen.add_widget(no_comments)

        yes_button = MDRaisedButton(text="Yes", theme_text_color="Custom", md_bg_color=[0,1,0,1], text_color=[0,0,0,1], pos_hint={"center_x": .4, "center_y": .2})
        def yes_snackbar(self, *args):
            def func(*args):
                blockchain.vote(1, str(searchbar.text))
                self.go_home(*args)
                return Snackbar(
                    text="You have voted yes",
                    snackbar_x="10dp",
                    snackbar_y="10dp",
                    size_hint_x=.3
                ).open()
            return func
        yes_button.bind(on_release=yes_snackbar(self))
        myscreen.add_widget(yes_button)
        
        no_button = MDRaisedButton(text="No", theme_text_color="Custom", md_bg_color=[1,0,0,1], text_color=[0,0,0,1], pos_hint={"center_x": .6, "center_y": .2})
        def no_snackbar(self, *args):
            def func(*args):
                blockchain.vote(-1, str(searchbar.text))
                self.go_home(*args)
                return Snackbar(
                    text="You have voted no",
                    snackbar_x="10dp",
                    snackbar_y="10dp",
                    size_hint_x=.5
                ).open()
            return func
        no_button.bind(on_release=no_snackbar(self))
        myscreen.add_widget(no_button)
        
        return myscreen
    
    def CCoin_Transaction_Page(self):
        myscreen = MDScreen(
            MDTopAppBar(
                title="CCoin Transaction",
                elevation=4,
                pos_hint={"top": 1},
                md_bg_color="#e7e4c0",
                specific_text_color="#4a4939",
                left_action_items=[
                    ['menu', lambda x: self.nav_drawer_open()]
                ],
            ),
            name="ccoin_transaction"
        )

        account_bar = MDTextField(icon_left="account", hint_text="User Public Key", pos_hint={"center_x":0.5, "center_y":0.8}, size_hint=[0.5,None])
        myscreen.add_widget(account_bar)

        ccoin_bar = MDTextField(icon_left="cash-multiple", hint_text="CCoin Amount", pos_hint={"center_x":0.5, "center_y":0.6}, size_hint=[0.5,None])
        myscreen.add_widget(ccoin_bar)

        send_button = MDRaisedButton(text="Send", theme_text_color="Custom", md_bg_color=[0,1,0,1], text_color=[0,0,0,1], pos_hint={"center_x": .5, "center_y": .4})
        send_button.bind(on_release=self.ccoin_submit(account_bar, ccoin_bar))
        myscreen.add_widget(send_button)

        #ccoin_public_key_label = MDLabel(text=blockchain.ccoin_public_key_str, halign="center", font_style="Caption", pos_hint={"center_x":0.5,"center_y":0.2})
        #myscreen.add_widget(ccoin_public_key_label)
        
        return myscreen
    
    def ccoin_submit(self, account_bar, ccoin_bar):
        def func(*args):
            res = blockchain.ccoin_transaction(account_bar.text, ccoin_bar.text)
            self.go_home(*args)
            if(res):
                return Snackbar(
                    text="You have issued the transaction",
                    snackbar_x="10dp",
                    snackbar_y="10dp",
                    size_hint_x=.5
                ).open()
            else:
                return Snackbar(
                    text="The transaction failed. Check account balance.",
                    snackbar_x="10dp",
                    snackbar_y="10dp",
                    size_hint_x=.5
                ).open()
        return func
    
    def Established_Law_Search_Page(self):
        global viewing_established_laws_short
        global viewing_established_laws_legal
        myscreen = MDScreen(name="established_law_search")

        toolbar = MDTopAppBar(
            title="Established Law Search",
            elevation=4,
            pos_hint={"top": 1},
            md_bg_color="#e7e4c0",
            specific_text_color="#4a4939",
            left_action_items=[
                ['menu', lambda x: self.nav_drawer_open()]
            ],
        )
        myscreen.add_widget(toolbar)

        searchbar = MDTextField(icon_left="magnify", pos_hint={"center_x":0.5, "center_y":0.85}, size_hint=[0.5,None])
        searchbar.bind(on_text_validate=self.search_established(searchbar, myscreen))
        myscreen.add_widget(searchbar)

        established_swiper = MDSwiper(size_hint_y=0.8, y=10)
        for i in range(len(viewing_established_laws_short)):
            local_item = MDSwiperItem(adaptive_height=True, md_bg_color = [1, 1, 1, 1], radius=20)
            local_layout = MDRelativeLayout()

            #local_img = FitImage(source="Icon.png", radius=20)
            #local_layout.add_widget(local_img)

            short_text_label = MDLabel(
                text=viewing_established_laws_short[i],
                font_style="H4",
                #size_hint_y=.1,
                halign="center",
                #valign="top",
                #height=self.texture_size[1],
                pos_hint={"center_y": .9},
                opposite_colors=True
            )
            local_layout.add_widget(short_text_label)

            legal_text_label = MDLabel(
                text=viewing_established_laws_legal[i],
                font_style="H6",
                halign="center",
                #size_hint_y=.1,
                #valign="top",
                #height=self.texture_size[1],
                pos_hint={"center_y": 0.5},
                opposite_colors=True
            )
            local_layout.add_widget(legal_text_label)

            local_item.add_widget(local_layout)
            established_swiper.add_widget(local_item)
        myscreen.add_widget(established_swiper)

        return myscreen
    
    def search_established(self, search_string, screen):
        def func(*args):
            global established_laws_short
            global viewing_established_laws_short
            global viewing_established_laws_legal
            if(search_string.text == ""):
                viewing_established_laws_short = established_laws_short[:]
                viewing_established_laws_legal = established_laws_legal[:]
            else:
                for i in range(len(viewing_established_laws_short)):
                    viewing_established_laws_short.pop()
                    viewing_established_laws_legal.pop()
                for i in range(len(established_laws_short)):
                    if(search_string.text.lower() in established_laws_short[i].lower()):
                        viewing_established_laws_short.append(established_laws_short[i])
                        viewing_established_laws_legal.append(established_laws_legal[i])
            self.screen_manager.remove_widget(self.established_law_search_page)
            self.established_law_search_page = self.Established_Law_Search_Page()
            self.screen_manager.add_widget(self.established_law_search_page)
            self.screen_manager.current = "established_law_search"

        return func
    
    
    def Proposed_Law_Search_Page(self):
        global viewing_proposed_laws_short
        global viewing_proposed_laws_legal
        global viewing_proposed_laws_hash
        global viewing_proposed_laws_pcoin

        myscreen = MDScreen(name="proposed_law_search")

        toolbar = MDTopAppBar(
                title="Proposed Law Search",
                elevation=4,
                pos_hint={"top": 1},
                md_bg_color="#e7e4c0",
                specific_text_color="#4a4939",
                left_action_items=[
                    ['menu', lambda x: self.nav_drawer_open()]
                ],
            )
        myscreen.add_widget(toolbar)

        searchbar = MDTextField(icon_left="magnify", pos_hint={"center_x":0.5, "center_y":0.85}, size_hint=[0.5,None])
        searchbar.bind(on_text_validate=self.search_proposed(searchbar, myscreen))
        myscreen.add_widget(searchbar)

        proposed_swiper = MDSwiper(size_hint_y=0.8, y=10)
        for i in range(len(viewing_proposed_laws_short)):
            local_item = MDSwiperItem(adaptive_height=True, md_bg_color = [1, 1, 1, 1], radius=20)
            local_layout = MDRelativeLayout()
            
            #local_img = FitImage(source="Icon.png", radius=20)
            #local_layout.add_widget(local_img)

            short_text_label = MDLabel(
                text=viewing_proposed_laws_short[i],
                font_style="H4",
                #size_hint_y=.1,
                #height=self.texture_size[1],
                halign="center",
                #valign="top",
                pos_hint={"center_y": 0.9},
                opposite_colors=True
            )
            local_layout.add_widget(short_text_label)

            legal_text_label = MDLabel(
                text=viewing_proposed_laws_legal[i],
                font_style="H6",
                #size_hint_y=.7,
                #height=self.texture_size[1],
                halign="center",
                #valign="top",
                pos_hint={"center_y": .5},
                opposite_colors=True
            )
            local_layout.add_widget(legal_text_label)

            pcoin_label = MDLabel(
                text="PCoin: "+str(viewing_proposed_laws_pcoin[i]),
                font_style="H6",
                #size_hint_y=None,
                #height=self.texture_size[1],
                halign="center",
                #valign="top",

                pos_hint={"center_y": .1, "center_x":0.2},
                opposite_colors=True
            )
            local_layout.add_widget(pcoin_label)

            donate_field = MDTextField(pos_hint={"center_x":0.5, "center_y":0.1}, text_color_normal=[0,0,1,1], halign="right", line_color_normal="blue", size_hint=[0.2,None])
            local_layout.add_widget(donate_field)

            donate_button = MDRaisedButton(text="Donate", pos_hint={"center_x": .8, "center_y": .1})
            def donate(self, donate_field, hash):
                def func(self, *args):
                    if(blockchain.pcoin_transaction(hash, int(donate_field.text))):
                        print(hash)
                        donation_amount = donate_field.text
                        donate_field.text = ""
                        return Snackbar(
                            text="You have donated: "+str(donation_amount),
                            snackbar_x="10dp",
                            snackbar_y="10dp",
                            size_hint_x=.3
                        ).open()
                    else:
                        return Snackbar(
                            text="Error... Please check your pcoin balance",
                            snackbar_x="10dp",
                            snackbar_y="10dp",
                            size_hint_x=.3
                        ).open()
                return func
            donate_button.bind(on_release=donate(self, donate_field, viewing_proposed_laws_hash[i]))
            local_layout.add_widget(donate_button)

            local_item.add_widget(local_layout)
            proposed_swiper.add_widget(local_item)
        myscreen.add_widget(proposed_swiper)

        return myscreen
    
    def search_proposed(self, search_string, screen):
        def func(*args):
            global proposed_laws_short
            global viewing_proposed_laws_short
            global proposed_laws_legal
            global viewing_proposed_laws_legal
            global proposed_laws_hash
            global viewing_proposed_laws_hash
            global proposed_laws_pcoin
            global viewing_proposed_laws_pcoin
            if(search_string.text == ""):
                viewing_proposed_laws_short = proposed_laws_short[:]
                viewing_proposed_laws_legal = proposed_laws_legal[:]
            else:
                for i in range(len(viewing_proposed_laws_short)):
                    viewing_proposed_laws_short.pop()
                    viewing_proposed_laws_legal.pop()
                    viewing_proposed_laws_hash.pop()
                    viewing_proposed_laws_pcoin.pop()
                for i in range(len(proposed_laws_short)):
                    if(search_string.text.lower() in proposed_laws_short[i].lower()):
                        viewing_proposed_laws_short.append(proposed_laws_short[i])
                        viewing_proposed_laws_legal.append(proposed_laws_legal[i])
                        viewing_proposed_laws_hash.append(proposed_laws_hash[i])
                        viewing_proposed_laws_pcoin.append(proposed_laws_pcoin[i])
            self.screen_manager.remove_widget(self.proposed_law_search_page)
            self.proposed_law_search_page = self.Proposed_Law_Search_Page()
            self.screen_manager.add_widget(self.proposed_law_search_page)
            self.screen_manager.current  = "proposed_law_search"

        return func
    
    
    def Draft_Laws_Page(self):
        myscreen = MDScreen(
                MDTopAppBar(
                    title="Draft Laws",
                    elevation=4,
                    pos_hint={"top": 1},
                    md_bg_color="#e7e4c0",
                    specific_text_color="#4a4939",
                    left_action_items=[
                        ['menu', lambda x: self.nav_drawer_open()]
                    ],
                ),
                name="draft_laws"
            )

        short_text = MDTextField(pos_hint={"center_x": 0.5, "center_y": .8}, halign="center", size_hint=[0.8, 0.2],  max_text_length=40, hint_text="Write Short Text", mode="fill", multiline=False, required=True, helper_text_mode="on_error", helper_text="Enter Proposed Law")
        myscreen.add_widget(short_text)

        law_text = MDTextField(pos_hint={"center_x": 0.5, "center_y": .45}, max_height=300, size_hint=[0.9, 0.45],  max_text_length=500, hint_text="Write The Law", mode="fill", multiline=True, required=True, helper_text_mode="on_error", helper_text="Enter Proposed Law")
        myscreen.add_widget(law_text)

        submit_button = MDRaisedButton(text="Submit", pos_hint={"center_x": 0.5, "center_y": .1})
        submit_button.bind(on_release=self.law_submit(short_text, law_text))
        myscreen.add_widget(submit_button)
        
        return myscreen
    
    def law_submit(self, short_text, law_text):
        def func(*args):
            res = blockchain.draft_law(short_text.text, law_text.text)
            self.go_home(*args)
            if(res):
                return Snackbar(
                    text="You have submitted the law",
                    snackbar_x="10dp",
                    snackbar_y="10dp",
                    size_hint_x=.5
                ).open()
            else:
                return Snackbar(
                    text="The submission failed!",
                    snackbar_x="10dp",
                    snackbar_y="10dp",
                    size_hint_x=.5
                ).open()
        return func
    

    def Manage_Connections_Page(self):
        myscreen = MDScreen(
                MDTopAppBar(
                    title="Manage Connections",
                    elevation=4,
                    pos_hint={"top": 1},
                    md_bg_color="#e7e4c0",
                    specific_text_color="#4a4939",
                    left_action_items=[
                        ['menu', lambda x: self.nav_drawer_open()]
                    ],
                ),
                name="manage_connections"
            )

        
        ip_text = MDTextField(pos_hint={"center_x": 0.5, "center_y": .7}, halign="center", size_hint=[0.8, 0.2],  max_text_length=40, hint_text="IP Address", mode="fill", multiline=False, required=True, helper_text_mode="on_error", helper_text="Enter Proposed Law")
        myscreen.add_widget(ip_text)

        def new_connection(ip_text):
            def func(*args):
                def func1(*args):
                    while(True):
                        blockchain.update_with_miner(ip_text.text)
                        blockchain.save()
                        time.sleep(10)
                res = blockchain.update_with_miner(ip_text.text)
                blockchain.save()
                t1 = threading.Thread(target=func1)
                t1.start()
                self.go_home(*args)
                if(res):
                    return Snackbar(
                        text="Chain Adopted",
                        snackbar_x="10dp",
                        snackbar_y="10dp",
                        size_hint_x=.5
                    ).open()
                else:
                    return Snackbar(
                        text="Invalid Chain!",
                        snackbar_x="10dp",
                        snackbar_y="10dp",
                        size_hint_x=.5
                    ).open()
            return func

        submit_button = MDRaisedButton(text="Connect", pos_hint={"center_x": 0.5, "center_y": .6})
        submit_button.bind(on_release=new_connection(ip_text))
        myscreen.add_widget(submit_button)

        ip_text = MDLabel(text="IP: "+str(get_ip()), halign="center", pos_hint={"center_x":0.5, "center_y":0.3})
        myscreen.add_widget(ip_text)
        
        server_button = MDRaisedButton(text="Become Server", pos_hint={"center_x": .5, "center_y": .2})
        def server(self, *args):
            def func(*args):
                global server_started
                if(server_started == False):
                    server_started = True
                    while(True):
                        blockchain.start_mining_server()
                        blockchain.mine()
            t1 = threading.Thread(target=func)
            t1.start()
            return Snackbar(
                text="Served",
                snackbar_x="10dp",
                snackbar_y="10dp",
                size_hint_x=.3
            ).open()
        server_button.bind(on_release=server)
        myscreen.add_widget(server_button)
        

        return myscreen
    
    
    def refresh(self):
        self.screen_manager.clear_widgets()

        #Home
        self.homepage = self.Homepage()
        self.screen_manager.add_widget(self.homepage)
        
        #Voting
        self.current_vote_page = self.Current_Vote_Page()
        self.screen_manager.add_widget(self.current_vote_page)
        
        #CCoin
        self.ccoin_transaction_page = self.CCoin_Transaction_Page()
        self.screen_manager.add_widget(self.ccoin_transaction_page)
        
        #Laws
        self.established_law_search_page = self.Established_Law_Search_Page()
        self.screen_manager.add_widget(self.established_law_search_page)
        
        self.proposed_law_search_page = self.Proposed_Law_Search_Page()
        self.screen_manager.add_widget(self.proposed_law_search_page)
        
        self.draft_laws_page = self.Draft_Laws_Page()
        self.screen_manager.add_widget(self.draft_laws_page)

        #Blockchain
        self.manage_connections_page = self.Manage_Connections_Page()
        self.screen_manager.add_widget(self.manage_connections_page)
        
        
    def switch_screen(self, instance_list_item: BaseNavigationDrawerItem):
        new_page = {"Home": "homepage", "Current Vote": "current_vote", "CCoin Transaction":"ccoin_transaction", "Search Established Laws":"established_law_search", "Search Proposed Laws":"proposed_law_search", "Draft Laws":"draft_laws", "Manage Connections":"manage_connections"}[instance_list_item.text]
        self.screen_manager.current = new_page
        if(new_page == "proposed_law_search"):
            update_proposed_laws()
        if(new_page == "established_law_search"):
            update_established_laws()
        if(new_page == "current_vote"):
            self.screen_manager.remove_widget(self.current_vote_page)
            self.current_vote_page = self.Current_Vote_Page()
            self.screen_manager.add_widget(self.current_vote_page)
            self.screen_manager.current = "current_vote"
        if(new_page == "homepage"):
            self.screen_manager.remove_widget(self.homepage)
            self.homepage = self.Homepage()
            self.screen_manager.add_widget(self.homepage)
            self.screen_manager.current = "homepage"
        self.navigation_drawer.set_state("close")
        
    def go_home(self, *args):
        self.screen_manager.remove_widget(self.homepage)
        self.homepage = self.Homepage()
        self.screen_manager.add_widget(self.homepage)
        self.screen_manager.current = "homepage"
        self.navigation_drawer.set_state("close")

    def show_alert_dialog(self, status):
        if not self.dialog:
            self.dialog = MDDialog(
                text="Discard draft?",
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                    ),
                    MDFlatButton(
                        text="DISCARD",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                    ),
                ],
            )
        self.dialog.open()

    def nav_drawer_open(self, *args):
        self.navigation_drawer.set_state("open")


EireneApp = Eirene()
EireneApp.run()