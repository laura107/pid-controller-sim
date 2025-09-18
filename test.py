from PyQt5.QtWidgets import QFormLayout, QScrollArea, QListWidget, QListWidgetItem, QWidget, QCheckBox, QTableWidgetItem, QHeaderView, QTableWidget, QPushButton, QLabel, QVBoxLayout, QDialog, QHBoxLayout, QSpacerItem, QSizePolicy, QLineEdit, QMessageBox, QListView, QInputDialog, QGridLayout, QGraphicsBlurEffect, QComboBox, QCompleter
from PyQt5.QtCore import QTimer, QDateTime, Qt, QSize, QStringListModel, QEvent, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QPixmap, QPainter, QIcon, QColor, QFontDatabase, QPalette
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from db_handler import Staff, LogEntry, Session, engine, Company, Group, Visitor
import os
import pycountry
from pinPadWidget import PinPadWidget

class TransparentButton(QPushButton):
    def __init__(self, image_path, text, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.text = text
        self.setFlat(True)
        self.setStyleSheet("background: transparent; border: none;")
        self.setIcon(QIcon(QPixmap(self.image_path)))
        self.setIconSize(QPixmap(self.image_path).size())
        self.setFixedSize(720, 125) 

    def paintEvent(self, event):
        painter = QPainter(self)
        pixmap = QPixmap(self.image_path)
        painter.drawPixmap(0, 0, self.width(), self.height(), pixmap)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont(self.font().family(), 28))
        painter.drawText(self.rect(), Qt.AlignCenter, self.text)
        super().paintEvent(event)
        
class GuestRegisterPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_active_user_label)
        self.timer.start(1000)  

        self.installEventFilter(self)  
        for widget in self.findChildren(QWidget): 
            widget.installEventFilter(self)
        
        self.pinpad = PinPadWidget(self)

        self.pinpad.setGeometry(200, 100, 400, 300) 
        self.pinpad.hide() 
        self.pinpad.access_granted.connect(self.on_access_granted) 
        
    def create_active_user_label(self):
        self.active_user_label = QLabel(self)
        self.active_user_label.setStyleSheet("""
            font-size: 18px;
            color: white;
            background: rgba(0, 0, 0, 0.6);
            padding: 10px;
            border-radius: 15px;
            font-weight: bold;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        """)
        self.active_user_label.setAlignment(Qt.AlignTop | Qt.AlignRight)
        self.active_user_label.setFixedWidth(200)
        
        self.update_active_user_label()
        return self.active_user_label

    def update_active_user_label(self):
        active_user_count = self.fetch_active_user_count()
        self.active_user_label.setText(f"OCCUPANTS: {active_user_count}  ")
        #print(f"Updated Active Users Label: {active_user_count}")  # Debug

    def fetch_active_user_count(self):
        session = Session()
        try:
            active_visitors = session.query(Visitor).filter_by(is_active=True).count()
            active_staff = session.query(LogEntry).filter(LogEntry.exit_time == None).count()
            return active_visitors + active_staff
        except Exception as e:
            print(f"Error fetching active user count: {e}")
            return 0
        finally:
            session.close()

    def paintEvent(self, event):
        painter = QPainter(self)
        pixmap = QPixmap(os.path.join(os.path.dirname(__file__), "backgrounds2/bg-blue3.png"))

        scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        target_rect = scaled_pixmap.rect()
        target_rect.moveCenter(self.rect().center())
        painter.drawPixmap(target_rect, scaled_pixmap)
        super().paintEvent(event)

    def initUI(self):
        self.showFullScreen()
        
        top_bar_layout = QHBoxLayout()
        top_bar_layout.setContentsMargins(0, 0, 0, 0)  
        top_bar_layout.setSpacing(0)
        top_bar_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        self.back_button = QPushButton("<", self)
        self.back_button.setStyleSheet("""
            font-size: 40px;
            color: white;
            background: rgba(0, 0, 0, 0.6);
            padding: 10px;
            border-radius: 15px;
            font-weight: bold;
        """)
        
        self.back_button.setFixedSize(75, 75) 
        x = 10  
        y = 10  
        
        self.back_button.move(x, y) 
        self.back_button.raise_() 

        self.back_button.setVisible(True)
        self.back_button.show()
        self.back_button.clicked.connect(self.go_back)

        font_thin_id = QFontDatabase.addApplicationFont(os.path.join(os.path.dirname(__file__), "fonts/Inter-Regular.ttf"))
        font_bold_id = QFontDatabase.addApplicationFont(os.path.join(os.path.dirname(__file__), "fonts/Inter-Bold.ttf"))
        
        if font_thin_id == -1 or font_bold_id == -1:
            print("Error loading font!")
        else:
            thin_font_family = QFontDatabase.applicationFontFamilies(font_thin_id)[0]
            bold_font_family = QFontDatabase.applicationFontFamilies(font_bold_id)[0]
            
            self.thin_font = QFont(thin_font_family)
            self.bold_font = QFont(bold_font_family)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        main_layout.addLayout(top_bar_layout)
        
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 50, 20, 0)
        top_layout.setAlignment(Qt.AlignTop | Qt.AlignRight)
        top_layout.addWidget(self.create_active_user_label())
        main_layout.addLayout(top_layout)

        self.stencil_label = QLabel(self)
        stencil_pixmap = QPixmap(os.path.join(os.path.dirname(__file__), "stencils/LogoBanner_2.png"))
        main_layout.addWidget(self.stencil_label)

        main_layout.setContentsMargins(190, 20, 20, 20)

        vertical_spacer_top = QSpacerItem(25, -50, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.insertItem(0, vertical_spacer_top)

        horizontal_spacer_left = QSpacerItem(10, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        main_layout.insertItem(0, horizontal_spacer_left)

        button_layout = QVBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.setSpacing(40)

        vertical_spacer_top = QSpacerItem(20, 350, QSizePolicy.Minimum, QSizePolicy.Expanding)
        button_layout.insertItem(0, vertical_spacer_top)

        button_layout.setContentsMargins(0, 0, 200, 0)

        horizontal_spacer_left = QSpacerItem(0, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
        main_layout.addItem(horizontal_spacer_left)

        self.staff_button = TransparentButton(os.path.join(os.path.dirname(__file__), "stencils/button.png"), "STAFF MANUAL SIGN IN", self)
        self.staff_button.clicked.connect(lambda: self.switch_page("Staff"))

        self.visitor_button = TransparentButton(os.path.join(os.path.dirname(__file__), "stencils/button.png"), "VISITOR MANUAL SIGN IN", self)
        self.visitor_button.clicked.connect(lambda: self.switch_page("Visitor"))

        self.newCard_button = TransparentButton(os.path.join(os.path.dirname(__file__), "stencils/button.png"), "REGISTER NEW CARD", self)
        self.newCard_button.clicked.connect(lambda: self.show_pinpad_and_switch())

        button_layout.addWidget(self.staff_button)
        button_layout.addWidget(self.visitor_button)
        button_layout.addWidget(self.newCard_button)

        main_layout.addLayout(button_layout)

        vertical_spacer_bottom = QSpacerItem(0, 500, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addItem(vertical_spacer_bottom)
        
    def show_pinpad_and_switch(self):
        self.pinpad.clear_pin()
        self.pinpad.show()
        self.pinpad.raise_() 

    def on_access_granted(self):
        self.pinpad.hide()  
        self.switch_page("newCard")  
        
    def switch_page(self, guest_type):
        if guest_type == "Staff":
            new_page = StaffSignInPage(parent_page=self) 
        elif guest_type == "Visitor":
            new_page = VisitorSignInPage(parent_page=self) 
            new_page.visitor_state_changed.connect(self.update_active_user_label)
        elif guest_type == "newCard":
            new_page = NewUserDetailsPage(parent_page=self) 

        self.parent().layout.addWidget(new_page)
        index = self.parent().layout.indexOf(new_page)
        self.parent().switch_screen(index)

    def go_back(self):
        self.parent().switch_screen(0)

    def eventFilter(self, obj, event):
        if event.type() in (QEvent.MouseButtonPress, QEvent.KeyPress):
            parent = self.parent()
            if parent and hasattr(parent, "reset_timeout_timer"):
                parent.reset_timeout_timer()
        return super().eventFilter(obj, event)
    
    def show_critical_popup(self, title, message):
        msg = QMessageBox(self)
        #msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)

        msg.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        ok_button = QPushButton("OK", msg)
        ok_button.setStyleSheet("""
            background-color: gray;
            color: white;
            padding: 10px;
            border-radius: 5px;
        """)
        msg.addButton(ok_button, QMessageBox.AcceptRole)

        msg.setStyleSheet("""
            background: rgba(0, 0, 0, 0.8);
            color: white;
            font-size: 16px;
            padding: 20px;
            border-radius: 10px;
        """)
        msg.exec_()

class StaffSignInPage(QWidget):    
    log_updated = pyqtSignal() 

    def __init__(self, parent_page=None):
        super().__init__(parent_page)
        self.parent_page = parent_page 
        self.initUI()
        
        self.installEventFilter(self)  
        for widget in self.findChildren(QWidget): 
            widget.installEventFilter(self)
            
    def paintEvent(self, event):
        painter = QPainter(self)
        pixmap = QPixmap(os.path.join(os.path.dirname(__file__), "backgrounds2/bg-blue3.png"))

        scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        target_rect = scaled_pixmap.rect()
        target_rect.moveCenter(self.rect().center())
        painter.drawPixmap(target_rect, scaled_pixmap)
        super().paintEvent(event)

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 2, 20, 25) 
        layout.setSpacing(20)
        
        top_right_layout = QHBoxLayout()
        top_right_layout.setContentsMargins(0, 2, 20, 20)
        top_right_layout.setAlignment(Qt.AlignTop | Qt.AlignRight)
        #top_right_layout.addWidget(self.parent_page.create_active_user_label())
        layout.addLayout(top_right_layout)
        
        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignCenter)  
        
        self.back_button = QPushButton("<", self)
        self.back_button.setStyleSheet("""
            font-size: 40px;
            color: white;
            background: rgba(0, 0, 0, 0.6);
            padding: 10px;
            border-radius: 15px;
            font-weight: bold;
        """)
        self.back_button.setFixedSize(75, 75) 
        x = 10  
        y = 10  
        
        self.back_button.move(x, y) 
        self.back_button.raise_() 

        self.back_button.setVisible(True)
        self.back_button.show()

        self.back_button.clicked.connect(self.go_back)

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("START TYPING YOUR SURNAME...")
        self.search_input.setStyleSheet("""
            font-size: 18px;
            padding: 12px;
            height: 65px;
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid rgba(255, 255, 255, 0.5);
            color: white;
            border-radius: 10px;
        """)
        self.search_input.setMinimumHeight(50)
        self.search_input.setFixedWidth(600)  
        self.search_input.textChanged.connect(self.search_surname)
        
        center_layout.addWidget(self.search_input)

        self.suggestions_list = QListView(self)
        self.suggestions_list.setStyleSheet("""
            background-color: #625afe;
            border: 2px solid white;
            border-radius: 10px;
            color: white;
            padding: 5px;
            font-size: 22px;
            selection-background-color: #4b4fd9;
            
            QListView::item {
                border: 2px solid transparent; 
                padding: 5px;
            }

            QListView::item:hover {
                border: 2px solid #ffffff;  
                background-color: #4b4fd9;  
            }

            QListView::item:selected {
                background-color: #4b4fd9;
                border: 2px solid #ffffff;
            }
        """)

        self.suggestions_list.setFixedHeight(120) 
        self.suggestions_list.setFixedWidth(600)  
        self.suggestions_list.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        spacer = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)
        center_layout.addItem(spacer)

        font_path = "fonts/SpaceGrotesk-Bold.ttf"
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            custom_font = QFont(font_family, 20) 
            self.suggestions_list.setFont(custom_font)
            
        model = QStringListModel()
        self.suggestions_list.setModel(model)

        center_layout.addWidget(self.suggestions_list)

        self.first_name_display = QLineEdit(self)
        self.first_name_display.setPlaceholderText("FIRST NAME")
        self.first_name_display.setReadOnly(True)
        self.first_name_display.setStyleSheet("""
            font-size: 30px;
            padding: 20px;
            height: 60px;
            background: rgba(255, 255, 255, 0.5);  
            border: 2px solid rgba(255, 255, 255, 0.7); 
            color: white;
            border-radius: 10px;
        """)

        self.first_name_display.setFixedWidth(600)  

        self.surname_display = QLineEdit(self)
        self.surname_display.setPlaceholderText("SURNAME")
        self.surname_display.setReadOnly(True)
        self.surname_display.setStyleSheet("""
            font-size: 30px;
            padding: 20px;
            height: 60px;
            background: rgba(255, 255, 255, 0.5); 
            border: 2px solid rgba(255, 255, 255, 0.7); 
            color: white;
            border-radius: 10px;
            cursor: not-allowed; 
        """)
        self.surname_display.setFixedWidth(600)

        self.company_display = QLineEdit(self)
        self.company_display.setPlaceholderText("COMPANY")
        self.company_display.setReadOnly(True)
        self.company_display.setStyleSheet("""
            font-size: 30px;
            padding: 20px;
            height: 60px;
            background: rgba(255, 255, 255, 0.5); 
            border: 2px solid rgba(255, 255, 255, 0.7); 
            color: white;
            border-radius: 10px;
            cursor: not-allowed; 
        """)
        self.company_display.setFixedWidth(600)

        center_layout.addWidget(self.first_name_display)
        center_layout.addWidget(self.surname_display)
        center_layout.addWidget(self.company_display)

        buttons_layout = QHBoxLayout()

        self.login_button = QPushButton("SIGN IN", self)
        self.login_button.setStyleSheet("""
            background-color: #A8E6CF; 
            color: white;
            padding: 20px;
            font-size: 50px;
            border-radius: 20px;
            width: 120px;
        """)
        self.login_button.setFixedWidth(280) 
        self.login_button.clicked.connect(self.on_sign_in_button_clicked) 
        

        self.logout_button = QPushButton("SIGN OUT", self)
        self.logout_button.setStyleSheet("""
            background-color: #FF8B8B; 
            color: white;
            padding: 20px;
            font-size: 50px;
            border-radius: 20px;
            width: 120px;
        """)
        self.logout_button.setFixedWidth(280)
        self.logout_button.clicked.connect(self.on_sign_out_button_clicked)

        buttons_layout.addWidget(self.login_button)
        buttons_layout.addWidget(self.logout_button)
        center_layout.addLayout(buttons_layout)

        font_path = "fonts/SpaceGrotesk-Bold.ttf"
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            custom_font = QFont(font_family, 18)
            self.login_button.setFont(custom_font)
            self.logout_button.setFont(custom_font)

        layout.addLayout(center_layout) 
        self.setLayout(layout)
        
    def go_back(self):
        self.parent().switch_screen(0)

    def eventFilter(self, obj, event):
        if event.type() in (QEvent.MouseButtonPress, QEvent.KeyPress):
            parent = self.parent()
            if parent and hasattr(parent, "reset_timeout_timer"):
                parent.reset_timeout_timer()
        return super().eventFilter(obj, event)
        
    def on_sign_in_button_clicked(self):
        first_name = self.first_name_display.text()
        surname = self.surname_display.text()
        company = self.company_display.text()
        self.search_input.clear()

        if not first_name or not surname:
            print("No staff selected.")
            self.show_critical_popup("SIGN IN ERROR", "PLEASE CLICK YOUR NAME BEFORE SIGNING IN")
            return

        session = sessionmaker(bind=engine)()
        try:
            # Check if staff exists
            staff = session.query(Staff).filter_by(FirstName=first_name, Surname=surname, Company=company).first()
            if not staff:
                self.show_critical_popup("ERROR", "STAFF MEMBER NOT FOUND IN DATABASE")
                return

            # Check for existing active log entry
            active_entry = session.query(LogEntry).filter_by(staff_id=staff.ID, exit_time=None).first()
            if active_entry:
                self.show_warning_popup(self, "ALREADY SIGNED IN", f"{first_name} {surname} HAS ALREADY BEEN SIGNED IN")
                return

            # Perform sign-in if no active session
            current_time = datetime.now()
            log_entry = LogEntry()
            log_entry.day = current_time.date()
            log_entry.entry_time = current_time.time()
            log_entry.staff_id = staff.ID
            session.add(log_entry)
            session.commit()
            
            # Show GreenScreen
            if hasattr(self.parent_page.parent(), 'green_screen'):
                green_screen = self.parent_page.parent().green_screen
                green_screen.setParent(None)
                green_screen.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Popup)
                green_screen.setGeometry(self.parent_page.geometry())
                green_screen.show_welcome_message(f"{first_name} {surname}")
                green_screen.show()
                QTimer.singleShot(3000, green_screen.hide)

            # Update active user label
            #self.parent_page.update_active_user_label()
            self.log_updated.emit() 


        except Exception as e:
            print(f"Error during manual sign-in: {e}")
            self.show_warning_popup("SIGN IN FAILED", "YOU ARE ALREADY SIGNED IN")
        finally:
            session.close()

    def show_warning_popup(self, title, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        
        msg.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        ok_button = QPushButton("OK", msg)
        ok_button.setStyleSheet("""
            background-color: #4CAF50;
            color: white;
            padding: 10px;
            border-radius: 5px;
        """)
        msg.addButton(ok_button, QMessageBox.AcceptRole)

        msg.setStyleSheet("""
            background: rgba(0, 0, 0, 0.8);
            color: white;
            font-size: 16px;
            padding: 20px;
            border-radius: 10px;
        """)
        msg.exec_()

    def on_sign_out_button_clicked(self):
        first_name = self.first_name_display.text()
        surname = self.surname_display.text()
        self.search_input.clear()

        if not first_name or not surname:
            print("No staff selected for sign-out.")
            self.show_critical_popup("Sign Out Error", "Please select a staff member before signing out.")
            return

        session = sessionmaker(bind=engine)()
        try:
            staff = session.query(Staff).filter_by(FirstName=first_name, Surname=surname).first()
            if not staff:
                print("Staff not found in the database.")
                self.show_critical_popup("Error", "Staff member not found.")
                return

            session.expire_all()

            # Look for an active log entry (no exit time set)
            log_entry = (
            session.query(LogEntry)
            .filter(LogEntry.staff_id == staff.ID)
            .filter(LogEntry.exit_time == None)
            .order_by(LogEntry.entry_time.desc())
            .first()
)

            if log_entry:
                log_entry.exit_time = datetime.now().time()
                session.commit()

                print(f"{first_name} {surname} signed out at {log_entry.exit_time}")

                if hasattr(self.parent_page.parent(), 'yellow_screen'):
                    yellow_screen = self.parent_page.parent().yellow_screen
                    yellow_screen.setParent(None)
                    yellow_screen.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Popup)
                    yellow_screen.setGeometry(self.parent_page.geometry())
                    yellow_screen.show_goodbye_message(f"{first_name} {surname}")
                    yellow_screen.show()
                    QTimer.singleShot(3000, yellow_screen.hide)
                else:
                    print("Yellow screen not found or initialized.")

                # Update the population count label
                #self.parent_page.update_active_user_label()
                self.log_updated.emit() 

            else:
                print(f"No active log entry found for {first_name} {surname}.")
                self.show_critical_popup("NO ACTIVE SESSION FOUND", f"{first_name} {surname} HAS NO ACTIVE SESSION, PLEASE SIGN IN TO CONTINUE")

        except Exception as e:
            print(f"Error during manual sign-out: {e}")
            self.show_warning_popup("SIGN OUT FAILED", "YOU ARE ALREADY SIGNED OUT")
            
    def show_critical_popup(self, title, message):
        msg = QMessageBox(self)
        #msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)

        msg.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        ok_button = QPushButton("OK", msg)
        ok_button.setStyleSheet("""
            background-color: gray;
            color: white;
            padding: 10px;
            border-radius: 5px;
        """)
        msg.addButton(ok_button, QMessageBox.AcceptRole)

        msg.setStyleSheet("""
            background: rgba(0, 0, 0, 0.8);
            color: white;
            font-size: 16px;
            padding: 20px;
            border-radius: 10px;
        """)
        msg.exec_()

    def restore_guest_register(self, original_geometry, screen):
        screen.hide()
        self.parent_page.setGeometry(original_geometry) 
        self.parent_page.raise_() 
        self.parent_page.activateWindow() 

    def search_surname(self):
        text = self.search_input.text()  
        if text:
            session = sessionmaker(bind=engine)()
            try:
                results = session.query(Staff).filter(Staff.Surname.ilike(f"{text}%")).all()

                if results:
                    matches = [f"{v.Surname}, {v.FirstName}, {v.Company}" for v in results]
                    model = QStringListModel(matches)

                    self.suggestions_list.setModel(model)
                    self.suggestions_list.setVisible(True)

                    self.suggestions_list.clicked.connect(self.on_suggestion_selected)
                else:
                    self.suggestions_list.setVisible(False)  
                    self.clear_user_details() 
            except Exception as e:
                print(f"Error fetching results: {e}")
            finally:
                session.close()
        else:
            self.suggestions_list.setVisible(False) 
            self.clear_user_details()  

    def on_suggestion_selected(self, index):
        selected_name = index.data()  
        self.search_input.setText(selected_name)

        surname, first_name, company = selected_name.split(', ') 
        session = sessionmaker(bind=engine)()
        try:
            staff = session.query(Staff).filter_by(Surname=surname, FirstName=first_name, Company=company).first()
            if staff:
                self.first_name_display.setText(staff.FirstName)
                self.surname_display.setText(staff.Surname)
                self.company_display.setText(staff.Company)
        except Exception as e:
            print(f"Error fetching visitor data: {e}")
        finally:
            session.close()

    def clear_user_details(self):
        self.first_name_display.clear()
        self.surname_display.clear()
        self.company_display.clear()
        
    def eventFilter(self, obj, event):
        if event.type() in (QEvent.MouseButtonPress, QEvent.KeyPress):
            parent = self.parent()
            if parent and hasattr(parent, "reset_timeout_timer"):
                parent.reset_timeout_timer()
        return super().eventFilter(obj, event)
        
class VisitorSignInPage(QWidget):
    visitor_state_changed = pyqtSignal()
    
    country_to_nationality = {
        'United Kingdom': 'BRITISH',
        'Ireland': 'IRISH',
        'United States': 'AMERICAN',
        'Canada': 'CANADIAN',
        'Australia': 'AUSTRALIAN',
        'Germany': 'GERMAN',
        'France': 'FRENCH',
        'Spain': 'SPANISH',
        'Italy': 'ITALIAN',
        'Mexico': 'MEXICAN',
        'Brazil': 'BRAZILIAN',
        'Argentina': 'ARGENTINE',
        'China': 'CHINESE',
        'India': 'INDIAN',
        'Japan': 'JAPANESE',
        'Russia': 'RUSSIAN',
        'South Korea': 'KOREAN',
        'South Africa': 'SOUTH AFRICAN',
        'Egypt': 'EGYPTIAN',
        'Nigeria': 'NIGERIAN',
        'Kenya': 'KENYAN',
        'Saudi Arabia': 'SAUDI',
        'Turkey': 'TURKISH',
        'Iran': 'IRANIAN',
        'Israel': 'ISRAELI',
        'Pakistan': 'PAKISTANI',
        'Bangladesh': 'BANGLADESHI',
        'Indonesia': 'INDONESIAN',
        'Vietnam': 'VIETNAMESE',
        'Thailand': 'THAI',
        'Malaysia': 'MALAYSIAN',
        'Singapore': 'SINGAPOREAN',
        'Philippines': 'FILIPINO',
        'New Zealand': 'NEW ZEALANDER',
        'Norway': 'NORWEGIAN',
        'Denmark': 'DANISH',
        'Finland': 'FINNISH',
        'Sweden': 'SWEDISH',
        'Iceland': 'ICELANDER',
        'Switzerland': 'SWISS',
        'Belgium': 'BELGIAN',
        'Netherlands': 'DUTCH',
        'Luxembourg': 'LUXEMBOURGISH',
        'Austria': 'AUSTRIAN',
        'Poland': 'POLISH',
        'Czech Republic': 'CZECH',
        'Hungary': 'HUNGARIAN',
        'Slovakia': 'SLOVAK',
        'Romania': 'ROMANIAN',
        'Bulgaria': 'BULGARIAN',
        'Serbia': 'SERBIAN',
        'Croatia': 'CROATIAN',
        'Slovenia': 'SLOVENE',
        'Bosnia and Herzegovina': 'BOSNIAN',
        'Montenegro': 'MONTENEGRIN',
        'Albania': 'ALBANIAN',
        'North Macedonia': 'MACEDONIAN',
        'Greece': 'GREEK',
        'Portugal': 'PORTUGUESE',
        'Andorra': 'ANDORRAN',
        'Monaco': 'MONACAN',
        'San Marino': 'SANMARINESE',
        'Vatican City': 'VATICAN',
        'Malta': 'MALTESE',
        'Cyprus': 'CYPRIOT',
        'Armenia': 'ARMENIAN',
        'Georgia': 'GEORGIAN',
        'Kazakhstan': 'KAZAKH',
        'Uzbekistan': 'UZBEK',
        'Turkmenistan': 'TURKMEN',
        'Kyrgyzstan': 'KYRGYZ',
        'Tajikistan': 'TAJIK',
        'Azerbaijan': 'AZERBAIJANI',
        'Moldova': 'MOLDOVAN',
        'Belarus': 'BELARUSIAN',
        'Ukraine': 'UKRAINIAN',
        'Lithuania': 'LITHUANIAN',
        'Latvia': 'LATVIAN',
        'Estonia': 'ESTONIAN',
        'Lichtenstein': 'LIECHTENSTEINIAN',
        'Palestine': 'PALESTINIAN',
        'Syria': 'SYRIAN',
        'Lebanon': 'LEBANESE',
        'Jordan': 'JORDANIAN',
        'Libya': 'LIBYAN',
        'Tunisia': 'TUNISIAN',
        'Algeria': 'ALGERIAN',
        'Morocco': 'MOROCCAN',
        'Mauritania': 'MAURITANIAN',
        'Western Sahara': 'SAHRAWI',
        'Sudan': 'SUDANESE',
        'Chad': 'CHADIAN',
        'Central African Republic': 'CENTRAL AFRICAN',
        'Cameroon': 'CAMEROONIAN',
        'Benin': 'BENINESE',
        'Togo': 'TOGOLESE',
        'Ghana': 'GHANAIAN',
        'Ivory Coast': 'IVORIAN',
        'Liberia': 'LIBERIAN',
        'Sierra Leone': 'SIERRA LEONEAN',
        'Guinea': 'GUINEAN',
        'Gabon': 'GABONESE',
        'Equatorial Guinea': 'EQUATORIAL GUINEAN',
        'Congo': 'CONGOLESE',
        'Democratic Republic of the Congo': 'CONGOLESE',
        'Uganda': 'UGANDAN',
        'Rwanda': 'RWANDAN',
        'Burundi': 'BURUNDIAN',
        'Tanzania': 'TANZANIAN',
        'Zambia': 'ZAMBIAN',
        'Zimbabwe': 'ZIMBABWEAN',
        'Angola': 'ANGOLAN',
        'Mozambique': 'MOZAMBICAN',
        'Namibia': 'NAMIBIAN',
        'Botswana': 'BOTSWANAN',
        'Lesotho': 'LESOTHOAN',
        'Swaziland': 'SWAZI',
        'Mauritius': 'MAURITIAN',
        'Seychelles': 'SEYCHELLOIS',
        'Comoros': 'COMORIAN',
        'Madagascar': 'MALAGASY',
        'Reunion': 'REUNIONESE',
        'Mayotte': 'MAYOTTEAN',
        'Cape Verde': 'CAPE VERDEAN',
        'Saint Helena': 'SAINT HELENIAN',
        'Ascension Island': 'ASCENSIONESE',
        'Trinidad and Tobago': 'TRINIDADIAN/TOBAGONIAN',
        'Barbados': 'BARBADIAN',
        'Saint Lucia': 'SAINT LUCIAN',
        'Saint Kitts and Nevis': 'KITTIAN/NEVISIAN',
        'Antigua and Barbuda': 'ANTIGUAN/BARBUDAN',
        'Dominica': 'DOMINICAN',
        'Grenada': 'GRENADIAN',
        'Saint Vincent and the Grenadines': 'VINCENTIAN',
        'Saint Pierre and Miquelon': 'SAINT-PIERRAIS/MIQUELONNAIS',
        'Bermuda': 'BERMUDIAN',
        'British Virgin Islands': 'VIRGIN ISLANDER',
        'Anguilla': 'ANGUILLIAN',
        'Montserrat': 'MONTSERRATIAN',
        'Turks and Caicos Islands': 'TURKS AND CAICOS ISLANDER',
        'Cayman Islands': 'CAYMANIAN',
        'Falkland Islands': 'FALKLAND ISLANDER',
        'Greenland': 'GREENLANDER',
        'Aruba': 'ARUBAN',
        'Curaçao': 'CURACAOAN',
        'Bonaire': 'BONAIREAN',
        'Sint Eustatius': 'SINT EUSTATIAN',
        'Saba': 'SABAN',
        'Guadeloupe': 'GUADELOUPEAN',
        'Martinique': 'MARTINIQUAIS',
        'French Guiana': 'GUYANAIS',
        'Saint Martin': 'SAINT-MARTINOIS',
        'Saint Barthélemy': 'SAINT BARTHÉLEMOIS'
}


    def __init__(self, parent_page=None):
        super().__init__(parent_page)
        self.parent_page = parent_page  
        self.visitor_scroll_area = QScrollArea()  
        self.selected_visitors = []

        self.initUI()

        self.installEventFilter(self)
        for widget in self.findChildren(QWidget):
            widget.installEventFilter(self)

    def initUI(self):
        self.main_layout = QVBoxLayout(self)  
        self.main_layout.setContentsMargins(10, 10, 10, 10) 
        self.main_layout.setSpacing(5)  

        top_right_layout = QHBoxLayout()
        top_right_layout.setContentsMargins(0, 20, 20, 0)
        top_right_layout.setAlignment(Qt.AlignTop | Qt.AlignRight)
        #if self.parent_page:
            #top_right_layout.addWidget(self.parent_page.create_active_user_label())
        self.main_layout.addLayout(top_right_layout)

        self.createHeader()
        self.createVisitorListSection()
        self.createFooter()
        self.setLayout(self.main_layout)
        
        self.back_button = QPushButton("<", self)
        self.back_button.setStyleSheet("""
            font-size: 40px;
            color: white;
            background: rgba(0, 0, 0, 0.6);
            padding: 10px;
            border-radius: 15px;
            font-weight: bold;
        """)
        self.back_button.setFixedSize(75, 75) 
        x = 10  
        y = 10  
        self.back_button.move(x, y) 
        self.back_button.raise_() 

        self.back_button.setVisible(True)
        self.back_button.show()

        self.back_button.clicked.connect(self.go_back)
        
    def go_back(self):
        self.parent().switch_screen(0)
        
    def resizeEvent(self, event):
        self.update()
        super().resizeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        pixmap = QPixmap(os.path.join(os.path.dirname(__file__), "backgrounds2/bg-blue3.png"))
        scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        target_rect = scaled_pixmap.rect()
        target_rect.moveCenter(self.rect().center())
        painter.drawPixmap(target_rect, scaled_pixmap)
        super().paintEvent(event)

    def eventFilter(self, obj, event):
        if event.type() in (QEvent.MouseButtonPress, QEvent.KeyPress):
            parent = self.parent()
            if parent and hasattr(parent, "reset_timeout_timer"):
                parent.reset_timeout_timer()
        return super().eventFilter(obj, event)

    def createHeader(self):
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignTop)
        header_layout.setSpacing(10)
        
        vertical_spacer = QSpacerItem(20, 120, QSizePolicy.Minimum, QSizePolicy.Fixed)
        header_layout.addItem(vertical_spacer)

        group_selection_layout = QVBoxLayout()
        group_selection_layout.setSpacing(20)
        group_selection_layout.setAlignment(Qt.AlignLeft)
        
        group_selection_layout.setContentsMargins(0, 60, 0, 0)  

        group_label = QLabel("SELECT GROUP:")
        group_label.setStyleSheet("""
            font-size: 24px;
            color: white;
            font-weight: bold;
        """)
        group_selection_layout.addWidget(group_label)
        
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10) 

        self.group_dropdown = QComboBox()
        self.group_dropdown.setFixedWidth(200)
        self.populateGroupDropdown()
        self.group_dropdown.setStyleSheet("""
            font-size: 18px;
            padding: 10px;
            background: rgba(255, 255, 255, 0.2);
            color: black;
            border: 2px solid rgba(255, 255, 255, 0.5);
            border-radius: 10px;
            selection-background-color: rgba(255, 255, 255, 0.3);
        """)
        self.group_dropdown.currentIndexChanged.connect(self.updateVisitorList)
        controls_layout.addWidget(self.group_dropdown)

        add_group_button = QPushButton("ADD GROUP")
        add_group_button.setFixedWidth(200)
        add_group_button.setStyleSheet("""
            font-size: 18px;
            padding: 15px;
            background: rgba(255, 255, 255, 0.3);
            color: white;
            border: 2px solid rgba(255, 255, 255, 0.5);
            border-radius: 10px;
            width: 180px;
        """)
        add_group_button.clicked.connect(self.addNewGroup)
        controls_layout.addWidget(add_group_button)

        header_layout.addLayout(controls_layout)
        self.main_layout.addLayout(header_layout)
        
    def show_critical_popup(self, title, message):
        msg = QMessageBox(self)
        #msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)

        msg.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        ok_button = QPushButton("OK", msg)
        ok_button.setStyleSheet("""
            background-color: gray;
            color: white;
            padding: 10px;
            border-radius: 5px;
        """)
        msg.addButton(ok_button, QMessageBox.AcceptRole)

        msg.setStyleSheet("""
            background: rgba(0, 0, 0, 0.8);
            color: white;
            font-size: 16px;
            padding: 20px;
            border-radius: 10px;
        """)
        msg.exec_()

    def populateGroupDropdown(self):
        session = Session()
        try:
            groups = session.query(Group).all()
            self.group_dropdown.clear()
            self.group_dropdown.addItems([group.name for group in groups])
        except Exception as e:
            print(f"Error populating group dropdown: {e}")
        finally:
            session.close()
            
    def addNewGroup(self):
        dialog = QInputDialog(self)
        dialog.setWindowTitle(" ") 
        dialog.setLabelText("ENTER GROUP NAME:")
        dialog.setInputMode(QInputDialog.TextInput)
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)  
        dialog.setStyleSheet("""
            QWidget {
                color: white;
                background-color: rgba(52, 52, 76, 0.85);
                font-size: 18px;
                border-radius: 15px;
            }
            QPushButton {
                color: white;
                background-color: rgba(52, 152, 219, 1);
                border-radius: 5px;
                padding: 10px;
                margin: 5px;
            }
            QLineEdit {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.5);
                border-radius: 5px;
                padding: 10px;
            }
        """)

        ok = dialog.exec_()
        group_name = dialog.textValue().strip()

        if ok and group_name:
            session = Session()
            existing_group = session.query(Group).filter_by(name=group_name).first()
            if existing_group:
                self.show_critical_popup("ERROR", "A GROUP WITH THIS NAME ALREADY EXISTS")
                session.close()
                return

            company_dialog = QInputDialog(self)
            company_dialog.setWindowTitle(" ") 
            company_dialog.setLabelText("ENTER VISITING COMPANY:")
            company_dialog.setInputMode(QInputDialog.TextInput)
            company_dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog) 
            company_dialog.setStyleSheet(dialog.styleSheet())

            ok = company_dialog.exec_()
            visiting_company = company_dialog.textValue().strip()

            if ok and visiting_company:
                new_group = Group(name=group_name, visiting_company=visiting_company)
                session.add(new_group)
                session.commit()
                self.customMessageBox("SUCCESS", f"GROUP '{group_name}' LOGGED SUCCESSFULLY", self.show_critical_popup)
                self.populateGroupDropdown()
            else:
                self.customMessageBox("ERROR", "NAME OF VISITING COMPANY IS REQUIRED", self.show_critical_popup)

            session.close()

    def customMessageBox(self, title, text, icon_type):
        msgBox = QMessageBox()
        msgBox.setWindowTitle(title)
        msgBox.setText(text)
        msgBox.setIcon(icon_type)
        msgBox.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog) 
        msgBox.setStyleSheet("""
            QMessageBox {
                background-color: rgba(52, 52, 76, 0.85);
                color: white;
                font-size: 16px;
                border-radius: 15px;
            }
            QPushButton {
                color: white;
                background-color: rgba(52, 152, 219, 1);
                border-radius: 5px;
                padding: 15px;
                margin: 10px;
            }
        """)
        msgBox.setMinimumSize(500, 400)
        msgBox.exec_()

    def createVisitorListSection(self):
        self.visitor_list_layout = QVBoxLayout()
        self.visitor_list_layout.setAlignment(Qt.AlignCenter)
        
        self.main_layout.setContentsMargins(20, 10, 20, 20)  
        self.main_layout.setSpacing(5)  

        self.visitor_list_layout.setSpacing(5)
        self.visitor_list_layout.setContentsMargins(5, 5, 5, 5)
        self.visitor_scroll_area.setFixedHeight(150)  

        list_header_label = QLabel("WELCOME VISITORS, SIGN IN OR OUT BELOW!")
        list_header_label.setAlignment(Qt.AlignCenter)
        list_header_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: white;
            background-color: rgba(52, 152, 219, 0.5);
            padding: 15px;
            border-radius: 10px;
        """)

        self.visitor_list_layout.addWidget(list_header_label)
        self.visitor_scroll_area = QScrollArea()
        self.visitor_scroll_area.setWidgetResizable(True)
        self.visitor_scroll_area.setStyleSheet("""
            background: rgba(255, 255, 255, 0.1);
            border: 0px solid rgba(255, 255, 255, 0.5);
            border-radius: 2px;
        """)
        self.visitor_scroll_area.setFixedWidth(800) 

        self.visitor_list_widget = QWidget()
        self.visitor_list_layout_grid = QVBoxLayout(self.visitor_list_widget)
        self.visitor_list_layout_grid.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.visitor_list_layout_grid.setSpacing(10)

        self.updateVisitorList()

        self.visitor_scroll_area.setWidget(self.visitor_list_widget)
        self.visitor_list_layout.addWidget(self.visitor_scroll_area)
        self.main_layout.addLayout(self.visitor_list_layout)

    def createFooter(self):
        footer_layout = QHBoxLayout()
        footer_layout.setAlignment(Qt.AlignCenter)
        footer_layout.setContentsMargins(510, 0, 10, 75)

        add_visitor_button = QPushButton("ADD NEW VISITOR")
        add_visitor_button.setFixedWidth(300)
        add_visitor_button.clicked.connect(self.addNewVisitorRow)

        sign_in_button = QPushButton("SIGN IN")
        sign_in_button.setFixedWidth(245)
        sign_in_button.clicked.connect(self.bulkSignIn)  # Connect bulk sign-in logic
        footer_layout.addWidget(sign_in_button)

        sign_out_button = QPushButton("SIGN OUT")
        sign_out_button.setFixedWidth(245)
        sign_out_button.clicked.connect(self.bulkSignOut)  # Connect bulk sign-out logic
        footer_layout.addWidget(sign_out_button)

        for btn in [add_visitor_button, sign_in_button, sign_out_button]:
            btn.setStyleSheet("""
                font-size: 25px;
                padding: 15px;
                background: rgba(255, 255, 255, 0.3);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.5);
                border-radius: 10px;
                width: 180px;
            """)
            footer_layout.addWidget(btn)

        self.main_layout.addLayout(footer_layout)


    def updateVisitorList(self):
        selected_group_name = self.group_dropdown.currentText()

        session = Session()
        selected_group = session.query(Group).filter_by(name=selected_group_name).first()
        session.close()

        if not selected_group:
            return

        for i in reversed(range(self.visitor_list_layout_grid.count())):
            widget = self.visitor_list_layout_grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        session = Session()
        visitors = session.query(Visitor).filter_by(group_id=selected_group.id).all()
        session.close()

        for visitor in visitors:
            self.addVisitorRow(visitor.first_name, visitor.surname, visitor.nationality, visitor_id=visitor.id, is_active=visitor.is_active)

    def addVisitorRow(self, first_name=None, last_name=None, nationality=None, visitor_id=None, is_active=False):
        row_layout = QHBoxLayout()
        row_layout.setSpacing(10)
        row_layout.setContentsMargins(0, 0, 0, 0)  # Remove any inner margins
        
        checkbox = QCheckBox()
        checkbox.setChecked(is_active)
        checkbox.stateChanged.connect(lambda state, vid=visitor_id: self.toggleSelectedVisitor(vid, state))
        checkbox.setStyleSheet("""
            border: none;
            margin-right: 10px;
        """)
        checkbox.setFixedSize(50, 50)
        row_layout.addWidget(checkbox)
        
        name_label = QLabel(f"{first_name} {last_name}")
        name_label.setStyleSheet("font-size: 22px; color: white;")
        row_layout.addWidget(name_label)
        
        nationality_label = QLabel(nationality or "N/A")
        nationality_label.setStyleSheet("font-size: 22px; color: white;")
        row_layout.addWidget(nationality_label)
        
        # Add stretch at the ends to ensure items take full width
        row_layout.addStretch()
        
        container_widget = QWidget()
        container_widget.setLayout(row_layout)
        container_widget.setStyleSheet("""
            background: transparent;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 5px;
            padding: 5px 0px;  # Minimise padding
        """)
        container_widget.setFixedWidth(self.visitor_scroll_area.width())  # Span the full width of the scroll area
        
        self.visitor_list_layout_grid.addWidget(container_widget)


        
    def toggleSelectedVisitor(self, visitor_id, state):
        if state == Qt.Checked:
            if visitor_id not in self.selected_visitors:
                self.selected_visitors.append(visitor_id)
        else:
            if visitor_id in self.selected_visitors:
                self.selected_visitors.remove(visitor_id)


    def bulkSignIn(self):
        if not self.selected_visitors:
            self.show_critical_popup("ERROR", "NO VISITORS SELECTED FOR SIGN IN")
            return

        session = Session()
        try:
            for visitor_id in self.selected_visitors:
                visitor = session.query(Visitor).filter_by(id=visitor_id).first()
                if visitor:
                    visitor.is_active = True  # Sign in
            session.commit()
            self.show_critical_popup("SUCCESS", "SELECTED VISITORS SIGNED IN SUCCESSFULLY")
            self.updateVisitorList()  # Refresh the list
        except Exception as e:
            print(f"Error during bulk sign-in: {e}")
        finally:
            session.close()
        self.selected_visitors.clear()  # Reset selection

    def bulkSignOut(self):
        if not self.selected_visitors:
            self.show_critical_popup("ERROR", "NO VISITORS SELECTED FOR SIGN OUT")
            return

        session = Session()
        try:
            for visitor_id in self.selected_visitors:
                visitor = session.query(Visitor).filter_by(id=visitor_id).first()
                if visitor:
                    visitor.is_active = False  # Sign out
            session.commit()
            self.show_critical_popup("SUCCESS", "SELECTED VISITORS SIGNED OUT SUCCESSFULLY")
            self.updateVisitorList()  # Refresh the list
        except Exception as e:
            print(f"Error during bulk sign-out: {e}")
        finally:
            session.close()
        self.selected_visitors.clear()  # Reset selection

        

    def update_visitor_active_state(self, visitor_id, state):
        session = Session()
        try:
            visitor = session.query(Visitor).filter_by(id=visitor_id).first()
            if visitor:
                visitor.is_active = (state == Qt.Checked)
                session.commit()
        except Exception as e:
            print(f"Error updating visitor state: {e}")
        finally:
            session.close()

    def addNewVisitorRow(self):
        if any(widget.objectName() == "new_visitor_row" for widget in self.findChildren(QWidget)):
            self.show_critical_popup("WARNING", "PLEASE COMPLETE ALL FIELDS")
            return

        row_layout = QHBoxLayout()
        row_layout.setSpacing(15)
        row_layout.setContentsMargins(5, 5, 5, 5) 

        first_name_input = QLineEdit()
        first_name_input.setPlaceholderText("FIRST NAME")
        first_name_input.setStyleSheet("""
            font-size: 18px;
            padding: 10px;
            background: rgba(255, 255, 255, 0.3);
            border: 2px solid rgba(255, 255, 255, 0.5);
            border-radius: 10px;
        """)

        surname_input = QLineEdit()
        surname_input.setPlaceholderText("SURNAME")
        surname_input.setStyleSheet("""
            font-size: 18px;
            padding: 10px;
            background: rgba(255, 255, 255, 0.3);
            border: 2px solid rgba(255, 255, 255, 0.5);
            border-radius: 10px;
        """)
        
        # Populate the nationalities list
        nationalities = []
        for country in pycountry.countries:
            country_name = country.name
            nationality = self.country_to_nationality.get(country_name, country_name)  # Correct reference
            nationalities.append(nationality)

        nationality_combo = QComboBox()
        nationality_combo.setStyleSheet("""
            font-size: 18px;
            padding: 5px;
            background: rgba(255, 255, 255, 0.3);
            border: 2px solid rgba(255, 255, 255, 0.5);
            border-radius: 10px;
        """)
        nationality_combo.setFixedWidth(150)
        nationality_combo.addItems(nationalities)

        save_button = QPushButton("SAVE")
        save_button.setStyleSheet("""
            font-size: 18px;
            padding: 10px;
            background-color: #3498db;
            color: white;
            border-radius: 10px;
        """)
        save_button.clicked.connect(lambda: self.saveNewVisitor(first_name_input, surname_input, nationality_combo))

        row_layout.addWidget(first_name_input, 1)
        row_layout.addWidget(surname_input, 1)
        row_layout.addWidget(nationality_combo, 1)
        row_layout.addWidget(save_button, 1)

        container_widget = QWidget()
        container_widget.setLayout(row_layout)
        container_widget.setObjectName("new_visitor_row")
        container_widget.setStyleSheet("""
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 10px;
        """)
        container_widget.setFixedWidth(800)

        self.visitor_list_layout_grid.addWidget(container_widget)


    def saveNewVisitor(self, first_name_input, surname_input, nationality_combo):
        first_name = first_name_input.text().strip()
        surname = surname_input.text().strip()
        nationality = nationality_combo.currentText().strip()

        if not first_name or not surname or not nationality:
            self.show_critical_popup("INPUT ERROR", "PLEASE FILL IN ALL FIELDS")
            return

        selected_group_name = self.group_dropdown.currentText()
        session = Session()
        selected_group = session.query(Group).filter_by(name=selected_group_name).first()

        if not selected_group:
            self.show_critical_popup("ERROR", "INVALID GROUP SELECTION")
            session.close()
            return

        new_visitor = Visitor(
            first_name=first_name,
            surname=surname,
            nationality=nationality,
            group_id=selected_group.id
        )
        session.add(new_visitor)
        session.commit()
        session.close()

        self.show_critical_popup("SUCCESS", f"NEW VISITOR {first_name} {surname} ADDED SUCCESSFULLY")
        self.updateVisitorList()

    def paintEvent(self, event):
        painter = QPainter(self)
        pixmap = QPixmap(os.path.join(os.path.dirname(__file__), "backgrounds2/bg-blue3.png"))
        painter.drawPixmap(self.rect(), pixmap)
        super().paintEvent(event)

    def eventFilter(self, obj, event):
        if event.type() in (QEvent.MouseButtonPress, QEvent.KeyPress):
            parent = self.parent()
            if parent and hasattr(parent, "reset_timeout_timer"):
                parent.reset_timeout_timer()
        return super().eventFilter(obj, event)
        
class NewUserDetailsPage(QWidget):
    
    country_to_nationality = {
        'United Kingdom': 'BRITISH',
        'Ireland': 'IRISH',
        'United States': 'AMERICAN',
        'Canada': 'CANADIAN',
        'Australia': 'AUSTRALIAN',
        'Germany': 'GERMAN',
        'France': 'FRENCH',
        'Spain': 'SPANISH',
        'Italy': 'ITALIAN',
        'Mexico': 'MEXICAN',
        'Brazil': 'BRAZILIAN',
        'Argentina': 'ARGENTINE',
        'China': 'CHINESE',
        'India': 'INDIAN',
        'Japan': 'JAPANESE',
        'Russia': 'RUSSIAN',
        'South Korea': 'KOREAN',
        'South Africa': 'SOUTH AFRICAN',
        'Egypt': 'EGYPTIAN',
        'Nigeria': 'NIGERIAN',
        'Kenya': 'KENYAN',
        'Saudi Arabia': 'SAUDI',
        'Turkey': 'TURKISH',
        'Iran': 'IRANIAN',
        'Israel': 'ISRAELI',
        'Pakistan': 'PAKISTANI',
        'Bangladesh': 'BANGLADESHI',
        'Indonesia': 'INDONESIAN',
        'Vietnam': 'VIETNAMESE',
        'Thailand': 'THAI',
        'Malaysia': 'MALAYSIAN',
        'Singapore': 'SINGAPOREAN',
        'Philippines': 'FILIPINO',
        'New Zealand': 'NEW ZEALANDER',
        'Norway': 'NORWEGIAN',
        'Denmark': 'DANISH',
        'Finland': 'FINNISH',
        'Sweden': 'SWEDISH',
        'Iceland': 'ICELANDER',
        'Switzerland': 'SWISS',
        'Belgium': 'BELGIAN',
        'Netherlands': 'DUTCH',
        'Luxembourg': 'LUXEMBOURGISH',
        'Austria': 'AUSTRIAN',
        'Poland': 'POLISH',
        'Czech Republic': 'CZECH',
        'Hungary': 'HUNGARIAN',
        'Slovakia': 'SLOVAK',
        'Romania': 'ROMANIAN',
        'Bulgaria': 'BULGARIAN',
        'Serbia': 'SERBIAN',
        'Croatia': 'CROATIAN',
        'Slovenia': 'SLOVENE',
        'Bosnia and Herzegovina': 'BOSNIAN',
        'Montenegro': 'MONTENEGRIN',
        'Albania': 'ALBANIAN',
        'North Macedonia': 'MACEDONIAN',
        'Greece': 'GREEK',
        'Portugal': 'PORTUGUESE',
        'Andorra': 'ANDORRAN',
        'Monaco': 'MONACAN',
        'San Marino': 'SANMARINESE',
        'Vatican City': 'VATICAN',
        'Malta': 'MALTESE',
        'Cyprus': 'CYPRIOT',
        'Armenia': 'ARMENIAN',
        'Georgia': 'GEORGIAN',
        'Kazakhstan': 'KAZAKH',
        'Uzbekistan': 'UZBEK',
        'Turkmenistan': 'TURKMEN',
        'Kyrgyzstan': 'KYRGYZ',
        'Tajikistan': 'TAJIK',
        'Azerbaijan': 'AZERBAIJANI',
        'Moldova': 'MOLDOVAN',
        'Belarus': 'BELARUSIAN',
        'Ukraine': 'UKRAINIAN',
        'Lithuania': 'LITHUANIAN',
        'Latvia': 'LATVIAN',
        'Estonia': 'ESTONIAN',
        'Lichtenstein': 'LIECHTENSTEINIAN',
        'Palestine': 'PALESTINIAN',
        'Syria': 'SYRIAN',
        'Lebanon': 'LEBANESE',
        'Jordan': 'JORDANIAN',
        'Libya': 'LIBYAN',
        'Tunisia': 'TUNISIAN',
        'Algeria': 'ALGERIAN',
        'Morocco': 'MOROCCAN',
        'Mauritania': 'MAURITANIAN',
        'Western Sahara': 'SAHRAWI',
        'Sudan': 'SUDANESE',
        'Chad': 'CHADIAN',
        'Central African Republic': 'CENTRAL AFRICAN',
        'Cameroon': 'CAMEROONIAN',
        'Benin': 'BENINESE',
        'Togo': 'TOGOLESE',
        'Ghana': 'GHANAIAN',
        'Ivory Coast': 'IVORIAN',
        'Liberia': 'LIBERIAN',
        'Sierra Leone': 'SIERRA LEONEAN',
        'Guinea': 'GUINEAN',
        'Gabon': 'GABONESE',
        'Equatorial Guinea': 'EQUATORIAL GUINEAN',
        'Congo': 'CONGOLESE',
        'Democratic Republic of the Congo': 'CONGOLESE',
        'Uganda': 'UGANDAN',
        'Rwanda': 'RWANDAN',
        'Burundi': 'BURUNDIAN',
        'Tanzania': 'TANZANIAN',
        'Zambia': 'ZAMBIAN',
        'Zimbabwe': 'ZIMBABWEAN',
        'Angola': 'ANGOLAN',
        'Mozambique': 'MOZAMBICAN',
        'Namibia': 'NAMIBIAN',
        'Botswana': 'BOTSWANAN',
        'Lesotho': 'LESOTHOAN',
        'Swaziland': 'SWAZI',
        'Mauritius': 'MAURITIAN',
        'Seychelles': 'SEYCHELLOIS',
        'Comoros': 'COMORIAN',
        'Madagascar': 'MALAGASY',
        'Reunion': 'REUNIONESE',
        'Mayotte': 'MAYOTTEAN',
        'Cape Verde': 'CAPE VERDEAN',
        'Saint Helena': 'SAINT HELENIAN',
        'Ascension Island': 'ASCENSIONESE',
        'Trinidad and Tobago': 'TRINIDADIAN/TOBAGONIAN',
        'Barbados': 'BARBADIAN',
        'Saint Lucia': 'SAINT LUCIAN',
        'Saint Kitts and Nevis': 'KITTIAN/NEVISIAN',
        'Antigua and Barbuda': 'ANTIGUAN/BARBUDAN',
        'Dominica': 'DOMINICAN',
        'Grenada': 'GRENADIAN',
        'Saint Vincent and the Grenadines': 'VINCENTIAN',
        'Saint Pierre and Miquelon': 'SAINT-PIERRAIS/MIQUELONNAIS',
        'Bermuda': 'BERMUDIAN',
        'British Virgin Islands': 'VIRGIN ISLANDER',
        'Anguilla': 'ANGUILLIAN',
        'Montserrat': 'MONTSERRATIAN',
        'Turks and Caicos Islands': 'TURKS AND CAICOS ISLANDER',
        'Cayman Islands': 'CAYMANIAN',
        'Falkland Islands': 'FALKLAND ISLANDER',
        'Greenland': 'GREENLANDER',
        'Aruba': 'ARUBAN',
        'Curaçao': 'CURACAOAN',
        'Bonaire': 'BONAIREAN',
        'Sint Eustatius': 'SINT EUSTATIAN',
        'Saba': 'SABAN',
        'Guadeloupe': 'GUADELOUPEAN',
        'Martinique': 'MARTINIQUAIS',
        'French Guiana': 'GUYANAIS',
        'Saint Martin': 'SAINT-MARTINOIS',
        'Saint Barthélemy': 'SAINT BARTHÉLEMOIS'
    }
    
    def __init__(self, parent_page=None, guest_type="NewCard"):
        super().__init__(parent_page)
        self.parent_page = parent_page 
        self.guest_type = guest_type
        self.initUI()

        self.installEventFilter(self)  
        for widget in self.findChildren(QWidget): 
            widget.installEventFilter(self)

    def paintEvent(self, event):
        painter = QPainter(self)
        pixmap = QPixmap(os.path.join(os.path.dirname(__file__), "backgrounds2/bg-blue3.png"))

        # Scale the pixmap to fit the widget while preserving the aspect ratio
        scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        # Center the image
        target_rect = scaled_pixmap.rect()
        target_rect.moveCenter(self.rect().center())

        # Draw the pixmap
        painter.drawPixmap(target_rect, scaled_pixmap)

        super().paintEvent(event)

    def initUI(self):
        layout = QVBoxLayout(self)
        
        layout.setContentsMargins(20, 150, 20, 10)
        layout.setSpacing(15)

        nationalities = []
        for country in pycountry.countries:
            country_name = country.name
            # Fetch the nationality from the dictionary if it exists
            nationality = self.country_to_nationality.get(country_name, country_name)  # Default to country name if no mapping found
            nationalities.append(nationality)
            
        self.nationality_combo = QComboBox(self)
        self.nationality_combo.setEditable(True)  # Allow text input and use a completer
        self.nationality_combo.setStyleSheet("""
            QComboBox {
                font-size: 22px; 
                padding: 14px;
                height: 50px;
                background: rgba(255, 255, 255, 0.1); 
                border: 2px solid rgba(255, 255, 255, 0.5); 
                color: white;
                border-radius: 10px;
                text-transform: uppercase;
                font-family: 'Space Grotesk', sans-serif; 
            }

            QComboBox QAbstractItemView {
                background: rgba(32, 32, 72, 0.95); 
                selection-background-color: rgba(72, 72, 112, 1); 
                selection-color: white;  
                color: white; 
                border: 1px solid rgba(255, 255, 255, 0.5); 
            }

            QComboBox::drop-down {
                border: none; 
                width: 40px; 
            }

            QComboBox::down-arrow {
                content: "\2193"; 
                font-size: 24px;  
                color: white; 
                width: 30px;
                height: 30px;
                padding-left: 5px; 
            }

            QLineEdit {
                font-size: 22px; 
                color: white;
                background: rgba(255, 255, 255, 0.1); 
                border: 2px solid rgba(255, 255, 255, 0.5); 
                border-radius: 10px; 
                padding: 12px;
            }
        """)

        self.nationality_combo.addItems(nationalities)
        completer = QCompleter(nationalities, self.nationality_combo)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self.nationality_combo.setCompleter(completer)

        self.nationality_combo.lineEdit().setPlaceholderText("NATIONALITY (E.G. BRITISH, AMERICAN...)")
        self.nationality_combo.setCurrentIndex(-1)  # Clear initial selection


        
        self.installEventFilter(self) 
        for widget in self.findChildren(QWidget): 
            widget.installEventFilter(self)

        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignCenter)
        center_layout.setSpacing(10) 

        top_right_layout = QHBoxLayout()
        top_right_layout.setContentsMargins(0, 0, 20, 0)
        top_right_layout.setAlignment(Qt.AlignTop | Qt.AlignRight)
        layout.addLayout(top_right_layout)

        self.back_button = QPushButton("<", self)
        self.back_button.setStyleSheet("""
            font-size: 40px;
            color: white;
            background: rgba(0, 0, 0, 0.6);
            padding: 10px;
            border-radius: 15px;
            font-weight: bold;
        """)
        self.back_button.setFixedSize(75, 75)

        x = 10 
        y = 10 
        self.back_button.move(x, y)  
        self.back_button.raise_() 

        self.back_button.setVisible(True)
        self.back_button.show()

        self.back_button.clicked.connect(self.go_back)

        scan_label = QLabel("SCAN NEW CARD ON THE READER", self)
        scan_label.setAlignment(Qt.AlignCenter)
        scan_label.setStyleSheet("""
            font-size: 22px;
            color: white;
            font-weight: bold;
            padding: 10px;
        """)
        center_layout.addWidget(scan_label)

        warning_label_top = QLabel("THIS WILL OVERRIDE ANY PREVIOUS CARD DATA", self)
        warning_label_top.setAlignment(Qt.AlignCenter)
        warning_label_top.setStyleSheet("""
            font-size: 25px;
            color: white;
            background-color: rgba(231, 76, 60, 0.8); 
            padding: 10px;
            border-radius: 15px;
        """)
        center_layout.addWidget(warning_label_top)

        self.first_name_input = QLineEdit(self)
        self.first_name_input.setPlaceholderText("FIRST NAME")
        self.first_name_input.setStyleSheet("""
            font-size: 18px;
            padding: 12px;
            height: 50px;
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid rgba(255, 255, 255, 0.5);
            color: white;
            border-radius: 10px;
        """)
        self.first_name_input.setFixedWidth(600)

        self.last_name_input = QLineEdit(self)
        self.last_name_input.setPlaceholderText("SURNAME")
        self.last_name_input.setStyleSheet("""
            font-size: 18px;
            padding: 12px;
            height: 50px;
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid rgba(255, 255, 255, 0.5);
            color: white;
            border-radius: 10px;
        """)
        self.last_name_input.setFixedWidth(600)

        self.company_input = QLineEdit(self)
        self.company_input.setPlaceholderText("COMPANY/ DEPARTMENT")
        self.company_input.setStyleSheet("""
            font-size: 18px;
            padding: 12px;
            height: 50px;
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid rgba(255, 255, 255, 0.5);
            color: white;
            border-radius: 10px;
        """)
        self.company_input.setFixedWidth(600)

        self.nationality_combo = QComboBox(self)
        self.nationality_combo.setEditable(True)  # Allow text input and use a completer
        self.nationality_combo.setStyleSheet("""
            QComboBox {
                font-size: 18px;
                padding: 12px;
                height: 50px;
                background: rgba(255, 255, 255, 0.1);
                border: 2px solid rgba(255, 255, 255, 0.5);
                color: white;
                border-radius: 10px;
                text-transform: uppercase;
                font-family: 'Space Grotesk', sans-serif;
            }

            QComboBox QAbstractItemView {
                background: rgba(32, 32, 72, 0.95);  
                selection-background-color: rgba(72, 72, 112, 1);  
                selection-color: white;  
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.5);
            }

            QComboBox::drop-down {
                border: none;
                width: 30px;
            }

            QComboBox::down-arrow {
                content: "\2193";
                font-size: 18px;
                color: white;
                width: 25px;
                height: 25px;
                padding-left: 5px;
            }
        """)

        self.nationality_combo.addItems(nationalities)
        completer = QCompleter(nationalities, self.nationality_combo)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self.nationality_combo.setCompleter(completer)

        self.nationality_combo.lineEdit().setPlaceholderText("NATIONALITY (E.G. BRITISH, AMERICAN...)")
        self.nationality_combo.setCurrentIndex(-1)

        # Additional form fields go here (as in your original code)
        self.uid_input = QLineEdit(self)
        self.uid_input.setPlaceholderText("UID")
        self.uid_input.setStyleSheet("""
            font-size: 18px;
            padding: 12px;
            height: 50px;
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid rgba(255, 255, 255, 0.5);
            color: white;
            border-radius: 10px;
        """)
        self.uid_input.setFixedWidth(600)

        center_layout.addWidget(self.first_name_input)
        center_layout.addWidget(self.last_name_input)
        center_layout.addWidget(self.company_input)
        center_layout.addWidget(self.nationality_combo)  
        center_layout.addWidget(self.uid_input)

        warning_label = QLabel("THIS WILL OVERRIDE ANY PREVIOUS CARD DATA", self)
        warning_label.setAlignment(Qt.AlignCenter)
        warning_label.setStyleSheet("""
            font-size: 25px;
            color: white;
            background-color: rgba(231, 76, 60, 0.8); 
            padding: 10px;
            border-radius: 15px;
        """)
        center_layout.addWidget(warning_label)

        self.register_button = QPushButton("REGISTER", self)
        self.register_button.setStyleSheet("""
            background-color: #3498db; 
            color: white;
            font-size: 22px;
            padding: 15px;
            border-radius: 10px;
            width: 120px;
        """)
        self.register_button.setFixedWidth(600)
        self.register_button.clicked.connect(self.register_user)
        center_layout.addWidget(self.register_button)

        bottom_spacer = QSpacerItem(80, 50, QSizePolicy.Minimum, QSizePolicy.Expanding)
        center_layout.addItem(bottom_spacer)

        spacer = QSpacerItem(80, 50, QSizePolicy.Minimum, QSizePolicy.Expanding)
        center_layout.addItem(spacer)

        center_layout.setContentsMargins(0, 20, 0, 0) 
        center_layout.setSpacing(20)

        font_path = "fonts/SpaceGrotesk-Bold.ttf"
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            custom_font = QFont(font_family, 18)
            self.register_button.setFont(custom_font)
            self.first_name_input.setFont(custom_font)
            self.last_name_input.setFont(custom_font)
            self.company_input.setFont(custom_font)
            self.nationality_combo.setFont(custom_font)  
            self.uid_input.setFont(custom_font)

        layout.addLayout(center_layout)
        self.setLayout(layout)

    def show_critical_popup(self, title, message):
        msg = QMessageBox(self)
        #msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)

        msg.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        ok_button = QPushButton("OK", msg)
        ok_button.setStyleSheet("""
            background-color: gray;
            color: white;
            padding: 10px;
            border-radius: 5px;
        """)
        msg.addButton(ok_button, QMessageBox.AcceptRole)

        msg.setStyleSheet("""
            background: rgba(0, 0, 0, 0.8);
            color: white;
            font-size: 16px;
            padding: 20px;
            border-radius: 10px;
        """)
        msg.exec_()

    def go_back(self):
        self.parent().switch_screen(0)

    def eventFilter(self, obj, event):
        if event.type() in (QEvent.MouseButtonPress, QEvent.KeyPress):
            parent = self.parent()
            if parent and hasattr(parent, "reset_timeout_timer"):
                parent.reset_timeout_timer()
        return super().eventFilter(obj, event)

    def populate_fields(self, first_name, last_name, company, nationality, uid):
        self.first_name_input.setText(first_name)
        self.last_name_input.setText(last_name)
        self.company_input.setText(company)
        self.nationality_combo.setText(nationality)
        self.uid_input.setText(uid)

    def register_user(self):
        uid = self.uid_input.text().strip()
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        company = self.company_input.text().strip()
        nationality = self.nationality_combo.currentText().strip()  

        if not uid:
            self.show_critical_popup("CARD SCAN REQUIRED", "PLEASE SCAN A CARD BEFORE REGISTERING")
            return

        if not first_name or not last_name or not company or not nationality:
            self.show_critical_popup("INPUT ERROR", "PLEASE FILL IN ALL FIELDS")
            return

        session = Session()
        try:
            # Check if UID already exists
            existing_staff = session.query(Staff).filter_by(RFID=uid).first()

            if existing_staff:
                self.show_critical_popup("DUPLICATE ENTRY", "THIS CARD HAS ALREADY BEEN REGISTERED")
                return

            # Register new staff if UID doesn't exist
            new_staff = Staff(
                FirstName=first_name,
                Surname=last_name,
                Company=company,
                RFID=uid,
                Nationality=nationality
            )
            session.add(new_staff)
            session.commit()

            self.show_critical_popup("REGISTRATION SUCCESSFUL", f"{first_name} {last_name} has been registered.")
            print(f"New user registered: {first_name} {last_name}, Company: {company}, Nationality: {nationality}")

        except IntegrityError:
            session.rollback()
            self.show_critical_popup("REGISTRATION ERROR", "ERROR REGISTERING USER")
        except Exception as e:
            session.rollback()
            self.show_critical_popup("REGISTRATION ERROR", f"UNEXPECTED ERROR: {str(e)}")
        finally:
            session.close()

    def clear_inputs(self):
        self.first_name_input.clear()
        self.last_name_input.clear()
        self.company_input.clear()
        self.nationality_combo.clear()
        
    def eventFilter(self, obj, event):
        if event.type() in (QEvent.MouseButtonPress, QEvent.KeyPress):
            parent = self.parent()
            if parent and hasattr(parent, "reset_timeout_timer"):
                parent.reset_timeout_timer()
        return super().eventFilter(obj, event)
    
    