import sys
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QCoreApplication, QRegExp
from PyQt5.QtGui import QRegExpValidator
import math
import ipaddress
from ipaddress import IPv4Address, IPv4Network, IPv4Interface, ip_address
from ip4LabV02 import *
import re
import clipboard as cp
import tkinter, tkinter.messagebox
from tkinter import filedialog
import time

class MyIPv4(IPv4Address):
    @property
    def binary_repr(self, sep=".") -> str:
        """Represent IPv4 as 4 blocks of 8 bits."""
        return sep.join(f"{i:08b}" for i in self.packed)

    @classmethod
    def from_binary_repr(cls, binary_repr: str):
        """Construct IPv4 from binary representation."""
        # Remove anything that's not a 0 or 1
        i = int(re.sub(r"[^01]", "", binary_repr), 2)
        return cls(i)

def IPAddress(IP: str) -> str:			#### Check if ip is special
    if (IPv4Address(IP).is_link_local):
        return "Link_local"
    if (IPv4Address(IP).is_multicast):
        return "Multicast"
    if (IPv4Address(IP).is_loopback):
        return "Loopback"
    if (IPv4Address(IP).is_reserved):
        return "Reserved"
    if (IPv4Address(IP).is_unspecified):
        return "Unspecified"
    if (IPv4Address(IP).is_private):
        return "Private" 
    if (IPv4Address(IP).is_global):
        return "Global"
def NearistNumber(number: str, AddTwo: bool) -> int:
	if not AddTwo:
		return math.ceil(math.log2(int(number)))
	if AddTwo:	
		return math.ceil(math.log2(int(number) + 2)) ## Add 2 for NW and Broadcasting Addresses 
def messagebox(title, text):
    root = tkinter.Tk()
    root.withdraw()
    tkinter.messagebox.showinfo(title, text)
    root.destroy()


class MyForm(QDialog):
	def __init__(self):
		super().__init__()
		self.ui = Ui_Dialog()
		self.ui.setupUi(self)
		self.ui.CIDR_FLSM.setChecked(True)
		self.ui.SubnetsSignificant.setChecked(True)
		self.ui.Mask.setValidator(QtGui.QIntValidator(0, 32, self))
		ipRange = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"   # Part of the regular expression
		ipRegex = QRegExp("^" + ipRange + "\\." + ipRange + "\\." + ipRange + "\\." + ipRange + "$") ###Thanks to Evgenij Legotskoj###
		ipValidator = QRegExpValidator(ipRegex, self)
		self.ui.IP.setValidator(ipValidator)
		self.ui.IP_A.setValidator(ipValidator)
		self.ui.IP_B.setValidator(ipValidator)
		self.ui.IP.editingFinished.connect(lambda:self.CheckMask(self.ui.IP.text(), self.ui.Mask.text(), 1))
		self.ui.IP_A.editingFinished.connect(lambda:self.CheckMask(self.ui.IP_A.text(), self.ui.Mask_A.text(),2))
		self.ui.IP_B.editingFinished.connect(lambda:self.CheckMask(self.ui.IP_B.text(), self.ui.Mask_B.text(),3))
		self.ui.ConBiDecPushButton.clicked.connect(self.Chnage_Bin_Dec)
		self.ui.GetIPAMaskPushButton.clicked.connect(self.GetMask)
		self.ui.CheckIPASpecialPushButton.clicked.connect(self.Special_IP)
		self.ui.GetIPANWBCPushButton.clicked.connect(self.Get_BroadcastAndNetworkIPs)
		self.ui.GetHostNetworkPushButton.clicked.connect(self.Host_Subnets_Numbers)
		self.ui.CheckAinsideBPushButton.clicked.connect(self.NetworkA_Inside_NetworkB)
		self.ui.GetAExcludingBPushButton.clicked.connect(self.RangeAwithoutB)
		self.ui.ExitPushButton.clicked.connect(QCoreApplication.instance().quit)
		self.ui.CalculatePushButton.clicked.connect(self.CaclulatingIPs)
		self.ui.CopyToClipboardQ.clicked.connect(self.CopyToClipboardQick)
		self.ui.CopyToClipboardR.clicked.connect(self.CopyToClipboardResult)
		self.ui.ClearWindow.clicked.connect(self.ClearWindowResult)
		self.ui.ClearQuickList.clicked.connect(self.ClearWindowQuick)
		self.ui.AboutPushButton.clicked.connect(self.HelpText) #For About/Help
		self.ui.SummaryCheckBox.setChecked(True)
		self.ui.AllRangesCheckBox.setChecked(False)
		self.ui.ExportResultsCheckBox.setChecked(False)
	

	def HelpText(self):
		msg = '''@ This code works ONLY with IP Version 4 @
This Code is developed by Mohamed Zakria, you can copy/modify this code as you wish.
Nevertheless, it's always great to keep credit for the original developer.
I'm not a coding expert, nor this is a strong/robust code, but hey it works! Well as long as you insert your data correctly.
This code, can performe CIDR/VLSM/FLSM notations + IP calculations, with adjustable hosts/subnet ranges.
I built this code to make it open source for all people and enthusiastics to enhance it's functions and build strong code.
We want to make a code that spares the Network & IT Engineers from the headache of calculations (I know they're enjoying it thu hahah).
Current Functions:
1. IP calculator (Decimal <-> Binary)
2. IP validation
3. Check if IP inside other Network
4. Get Masks + NW and Broadcast IPs
5. Check if IP in special range (ex. loopback)
6. Get Hosts and Subnet numbers in a given IP
7. Make CIDR/FLSM notations (adjustable ranges)
8. Make CIDR/VLSM notations (adjustable ranges)
9. Autofill/calcualte (Hosts or subnets) whenever either is blank (with Max possible numbers)
10.Autofill Mask label
11.Export results in txt file
12.Display summary/limited ranges (ones you entered hosts/subnets) or all possible range

#Thanks to Evgenij Legotskoj from EVILEG For the IP Validator suggestions'''
		
		messagebox('About', msg)

	def Summary(self, _hosts, _subnets):
		message1 = 'The Total # of Networks: ' + str(_subnets)
		message2 = 'The Total # of Hosts: {} including NW & BC'.format(str(_hosts))
		self.ui.ResultsList.addItem('-------------------------------------------------- #')
		self.ui.ResultsList.addItem(message1)
		self.ui.ResultsList.addItem(message2)
		self.ui.ResultsList.addItem('-------------------------------------------------- #')

	def CopyToClipboardResult(self):
		ResultsCopy = '' #Will hold all values in Results window
		for i in range(self.ui.ResultsList.count()):
			ResultsCopy += str(self.ui.ResultsList.item(i).text()) + '\n'
		cp.copy(ResultsCopy)

	def CopyToClipboardQick(self):
		ResultsCopy = '' #Will hold all values in Results window
		for i in range(self.ui.QuickResultsList.count()):
			ResultsCopy += str(self.ui.QuickResultsList.item(i).text()) + '\n'
		cp.copy(ResultsCopy)

	def ClearWindowQuick(self):
		# if (keyboard.read_key()).upper() == "C":
		self.ui.QuickResultsList.clear()

	def ClearWindowResult(self):
		# if (keyboard.read_key()).upper() == "C":
		self.ui.ResultsList.clear()

	def CaclulatingIPs(self):

		IP_MASK = self.ui.IP.text() + '/' + self.ui.Mask.text() #IP/Mask Format for an IP
		if int(self.ui.Mask.text()) >32 or int(self.ui.Mask.text()) <=1:
			messagebox('Fatal Error', 'Check your Mask First!')
			return
		elif int(self.ui.Mask.text()) == 31 or int(self.ui.Mask.text()) == 32:
			a = list(ipaddress.ip_network(IP_MASK).hosts())
			self.ui.ResultsList.addItem('Subnet # '+IP_MASK)
			for i in a:
				self.ui.ResultsList.addItem(str(i))
			return

		inAllRange = self.ui.AllRangesCheckBox.isChecked()
		_Subnet = 0
		_Host = 0

		if self.ui.SubnetsSpinBox.value() == 0 and len(self.ui.HostsNumber.text()) ==0:
			messagebox('Warning', 'Host and Subnet values are missing\nAll addresses will be outlined!')
			self.ui.ResultsList.addItem('Subnet #' + IP_MASK)
			for x in ipaddress.ip_network(IP_MASK, False):
				self.ui.ResultsList.addItem(str(x))
			if self.ui.ExportResultsCheckBox.isChecked() == True:
				root = tkinter.Tk()
				root.withdraw()
				root.attributes('-topmost', True) #Make Window on top of opened applications.
				file_path = filedialog.askdirectory()
				ts = time.time()
				FileName = 'Results of {} #{}.txt'.format(self.ui.IP.text(), str(ts).split('.')[0])

				with open(file_path + '\\' + FileName, 'w') as output:
					for i in range(self.ui.ResultsList.count()):
						output.write(self.ui.ResultsList.item(i).text() + '\n')
			return #Abort the rest of the function

		if self.ui.CIDR_FLSM.isChecked():
			SubnetsNumberVar = self.ui.SubnetsSpinBox.value()
			if ',' in self.ui.HostsNumber.text():
				temp = self.ui.HostsNumber.text()
				HostsNumberVar = (temp.split(','))[0] #Take the first part of the inputs
			else:
				HostsNumberVar = self.ui.HostsNumber.text()

			if len(HostsNumberVar) != 0 and SubnetsNumberVar!=0:
				SubnetNearistNumber = NearistNumber(SubnetsNumberVar, False)
				HostsNearistNumber = NearistNumber(HostsNumberVar, True)
				#print('S= {}, H= {}'.format(SubnetNearistNumber, HostsNearistNumber))
			else:
				if SubnetsNumberVar == 0:
					self.ui.SubnetsSignificant.setChecked(False)
					self.ui.HostsSignificant.setChecked(True)

					#SubnetNearistNumber = NearistNumber(SubnetsNumberVar, False)
					HostsNearistNumber = NearistNumber(HostsNumberVar, False) #Not neccessarliy to add 2 here (False)
					temp = 32 - (int(self.ui.Mask.text()) + HostsNearistNumber)
					#print('Temp for Subnet= {}, Hosts bits = {}'.format(str(temp), str(HostsNearistNumber)))
					SubnetNearistNumber = 2**temp #NearistNumber(str(2**temp), False)
					self.ui.SubnetsSpinBox.setValue(SubnetNearistNumber)
				elif len(HostsNumberVar) == 0:
					self.ui.HostsSignificant.setChecked(False)
					self.ui.SubnetsSignificant.setChecked(True)

					SubnetNearistNumber = NearistNumber(SubnetsNumberVar, False)
					#HostsNearistNumber = NearistNumber(HostsNumberVar, True)
					temp = 32 - (int(self.ui.Mask.text()) + SubnetNearistNumber)
					HostsNearistNumber = 2**temp #NearistNumber(str(2**temp), True)
					self.ui.HostsNumber.setText(str(2**temp))

			if (SubnetNearistNumber + HostsNearistNumber + int (self.ui.Mask.text())) > 32:
				#print('Tag1')
				NewSubnet = 0
				if self.ui.SubnetsSignificant.isChecked():
					#print('Tag2')
					NewSubnet = int(self.ui.Mask.text()) + SubnetNearistNumber
					NetworkComponents = list(ipaddress.ip_network(IP_MASK, False).subnets(new_prefix=NewSubnet))
					counter = 0
					for i in NetworkComponents:
						if counter == int(self.ui.SubnetsSpinBox.value()) and not inAllRange:
							break #Display only users required portion of Subnets.
						else:	  #Displays all possible hosts
							self.ui.ResultsList.addItem('Subnet # {}'.format(str(i)))
							Matrix = []
							for x in list(ipaddress.ip_network(i)):
								#self.ui.ResultsList.addItem(str(x))
								Matrix.append(str(x)) #Stores current IP
								_Host =+ 1
							self.ui.ResultsList.addItem('Network IP: {} ~ Broadcast IP: {}'.format(str(i.network_address), str(i.broadcast_address)))
							self.ui.ResultsList.addItem('Range: {} ~ {}'.format(str(Matrix[1]), str(Matrix[len(Matrix) - 2])))
						counter +=1 #Care about Subnets only (How many iterations of Host bist)
						_Subnet +=1

				if self.ui.HostsSignificant.isChecked():
					NewSubnet = 32 - (HostsNearistNumber) #Consider all bits or (Mask + New prefix) is ONE to make new prefix
					NetworkComponents = list(ipaddress.ip_network(IP_MASK, False).subnets(new_prefix=NewSubnet))
					
					for i in NetworkComponents:
						counter = 0 #Counting Hosts per Subnet
						#NewNetworkHosts = list(ipaddress.ip_network(i).hosts())
						self.ui.ResultsList.addItem('Subnet # {}'.format(str(i)))
						Matrix = []
						#self.ui.ResultsList.addItem(str(i.network_address))
						
						for n in i:
							if counter == int(HostsNumberVar) and not inAllRange: #when Hosts number equals user entry, break.
								break
							else:
								#self.ui.ResultsList.addItem(str(n))
								Matrix.append(str(n))
								_Host+=1
							counter +=1
						self.ui.ResultsList.addItem('Network IP: {} ~ Broadcast IP: {}'.format(str(i.network_address), str(i.broadcast_address)))
						self.ui.ResultsList.addItem('Range: {} ~ {}'.format(str(Matrix[1]), str(Matrix[len(Matrix) - 2])))
						_Subnet+=1

			else:
				NewSubnet = int(self.ui.Mask.text()) + SubnetNearistNumber
				NetworkComponents = list(ipaddress.ip_network(IP_MASK, False).subnets(new_prefix=NewSubnet))
				HostsCounter =0 		#Breaks when hosts equal user entry
				SubnetsCounter =0 		#Breaks when subnets equal user entry.
				for net in NetworkComponents:
					if SubnetsCounter == SubnetsNumberVar and not inAllRange:
						break
					else:
						self.ui.ResultsList.addItem('Subnet # {}'.format(str(net)))
						# self.ResultsCopyR += self.ui.ResultsList.item(self.ui.ResultsList.count() - 1).text() + '\n'
						HostsCounter =0
						Matrix = []
						for host in net:
							if HostsCounter == int(HostsNumberVar) + 1 and not inAllRange: #Get NW and BC IPs as well
								#self.ui.ResultsList.addItem(str(net.broadcast_address)) #Display the broadcast first then break
								break
							else:
								#self.ui.ResultsList.addItem(str(host))
								Matrix.append(str(host))
								_Host+=1
								# self.ResultsCopyR += self.ui.ResultsList.item(self.ui.ResultsList.count() - 1).text() + '\n'
							HostsCounter += 1
						self.ui.ResultsList.addItem('Network IP: {} ~ Broadcast IP: {}'.format(str(net.network_address), str(net.broadcast_address)))
						if str(Matrix[len(Matrix) - 1]) == str(net.broadcast_address):
							self.ui.ResultsList.addItem('Range: {} ~ {}'.format(str(Matrix[1]), str(Matrix[len(Matrix) - 2])))
						else:
							self.ui.ResultsList.addItem('Range: {} ~ {}'.format(str(Matrix[1]), str(Matrix[len(Matrix) - 1])))
					SubnetsCounter +=1
					_Subnet+=1

		if self.ui.CIDR_VLSM.isChecked(): 
			VLSM_HostsNumbers = []
			#s.strip()
			temp = (re.sub(r"\s+", "", self.ui.HostsNumber.text())).split(',')
			NonCommaHostsNumber = list(filter(None, temp))
			TotalHosts = 0 #Summation of total hosts to check for validity
			for i in NonCommaHostsNumber:
				VLSM_HostsNumbers.append(int(i))
				TotalHosts += int(i)
			VLSM_HostsNumbers = sorted(VLSM_HostsNumbers, reverse=True)
			##Exception When number of subnets DOES NOT Equal host items. 
			if self.ui.SubnetsSpinBox.value() == len(VLSM_HostsNumbers):
				if (NearistNumber(TotalHosts, False) + int(self.ui.Mask.text())) <=32:
					for subnet in VLSM_HostsNumbers:
						NewBitsForHosts = NearistNumber(subnet, True)
						NewTotalMask = 32 - NewBitsForHosts #Represents the New Total Mask
						NetworkComponents = list(ipaddress.ip_network(IP_MASK, False).subnets(new_prefix=NewTotalMask))
						#for net in NetworkComponents: #This for loop for the Subnets (we only need the first one)
						Counter = 0 #Track only hosts number
						self.ui.ResultsList.addItem('Subnet # {} # For Hosts: {}'.format(str(NetworkComponents[0]),subnet))
						Matrix = []
						for addr in NetworkComponents[0]: 		  #This one for hosts
							net = NetworkComponents[0]
							if Counter == (subnet + 1) and not inAllRange: #the Network ID is not considered (+1)
								#self.ui.ResultsList.addItem(str(NetworkComponents[0].broadcast_address)) #Display the BC address of the current NW
								break
							else:
								#Number of Hosts & Networks
								#self.ui.ResultsList.addItem(str(addr))
								Matrix.append(str(addr))
								_Host+=1
							Counter +=1
						self.ui.ResultsList.addItem('Network IP: {} ~ Broadcast IP: {}'.format(str(net.network_address), str(net.broadcast_address)))
						if str(Matrix[len(Matrix) - 1]) == str(net.broadcast_address):
							self.ui.ResultsList.addItem('Range: {} ~ {}'.format(str(Matrix[1]), str(Matrix[len(Matrix) - 2])))
						else:
							self.ui.ResultsList.addItem('Range: {} ~ {}'.format(str(Matrix[1]), str(Matrix[len(Matrix) - 1])))
						_Subnet+=1
						IP_MASK = str(NetworkComponents[0].broadcast_address + 1) + '/' + str(NetworkComponents[0].prefixlen) #Change the NW Address to the New one

				else: # Make SuperNetting!
					print('Mask is big')
					SuperNetwPrefixDiff = int(self.ui.Mask.text()) + NearistNumber(TotalHosts,False) - 32
					NewSuperNet = ipaddress.ip_network(IP_MASK, False).supernet(prefixlen_diff=SuperNetwPrefixDiff)
					self.ui.ResultsList.addItem('$SuperNet was Called @ : {}'.format(str(NewSuperNet)))
					for subnet in VLSM_HostsNumbers:
						NewBitsForHosts = NearistNumber(subnet, True)
						NewTotalMask = 32 - NewBitsForHosts #Represents the New Total Mask
						NetworkComponents = list(NewSuperNet.subnets(new_prefix=NewTotalMask))
						#for net in NetworkComponents: #This for loop for the Subnets (we only need the first one)
						self.ui.ResultsList.addItem('Subnet # {} # For Hosts: {}'.format(str(NetworkComponents[0]),subnet))
						Counter = 0
						Matrix = []
						for addr in NetworkComponents[0]: 		  #This one for hosts
							net = NetworkComponents[0]
							if Counter == (subnet + 1) and not inAllRange: #the Network ID is not considered (+1)
								#self.ui.ResultsList.addItem(str(NetworkComponents[0].broadcast_address))
								break
							#Number of Hosts & Networks
							else:
								#self.ui.ResultsList.addItem(str(addr))
								Matrix.append(str(addr))
								_Host+=1
							#NW BC
							Counter+=1
						self.ui.ResultsList.addItem('Network IP: {} ~ Broadcast IP: {}'.format(str(net.network_address), str(net.broadcast_address)))
						if str(Matrix[len(Matrix) - 1]) == str(net.broadcast_address):
							self.ui.ResultsList.addItem('Range: {} ~ {}'.format(str(Matrix[1]), str(Matrix[len(Matrix) - 2])))
						else:
							self.ui.ResultsList.addItem('Range: {} ~ {}'.format(str(Matrix[1]), str(Matrix[len(Matrix) - 1])))
						_Subnet+=1
						NewSuperNet = ipaddress.ip_network(str(NetworkComponents[0].broadcast_address + 1) + '/' + str(NetworkComponents[0].prefixlen)) #Change the NW Address to the New one

			else:
				messagebox('Error', 'Make sure the Subnets equal Hosts number')
				pass
		if self.ui.SummaryCheckBox.isChecked() == True:
			self.Summary(_Host, _Subnet)

		if self.ui.ExportResultsCheckBox.isChecked() == True:
			root = tkinter.Tk()
			root.withdraw()
			root.attributes('-topmost', True) #Make Window on top of opened applications.
			file_path = filedialog.askdirectory()
			ts = time.time()
			FileName = 'Results of {} #{}.txt'.format(self.ui.IP.text(), str(ts).split('.')[0])
			try:
				with open(file_path + '\\' + FileName, 'w') as output:
					for i in range(self.ui.ResultsList.count()):
						output.write(self.ui.ResultsList.item(i).text() + '\n')
			except:
				messagebox('Error', 'No Folder was selected\nAbort Exporting')

	def RangeAwithoutB(self):
		try:
			ipA = self.ui.IP_A.text() + '/' + self.ui.Mask_A.text()
			ipB = self.ui.IP_B.text() + '/' + self.ui.Mask_B.text()
			a = ipaddress.ip_network(ipA, False)
			b = ipaddress.ip_network(ipB, False)
			try:
				NewRange = list(a.address_exclude(b))
			except ValueError:
				messagebox('Intersection Error','Network B is not completely contained in network A')
				return
			if NewRange:
				self.ui.QuickResultsList.addItem('@ -----Network: {} Excluding Network: {}'.format(str(ipA),str(ipB)))
				counter = 0 ## Holds Subnetwork Addresses
				Matrix = []
				for n in NewRange:
					self.ui.QuickResultsList.addItem('Subnet # '+str(n))
					for i in n:
						#self.ui.QuickResultsList.addItem(str(i))
						Matrix.append(str(i))
						#print(str(i))
						counter+=1
					self.ui.QuickResultsList.addItem('Network IP: {} ~ Broadcast IP: {}'.format(str(n.network_address), str(n.broadcast_address)))
					self.ui.QuickResultsList.addItem('Range: {} ~ {}'.format(str(Matrix[1]), str(Matrix[len(Matrix) - 2])))
				#self.ui.QuickResultsList.addItem(' ----- # {} NW and {} Total Addresses were found -----'.format(str(len(NewRange)), str(counter)))
		except:
			messagebox('Error', 'Insert valid IPs first!')

	def NetworkA_Inside_NetworkB(self):
		try:
			ipA = self.ui.IP_A.text() + '/' + self.ui.Mask_A.text()
			ipB = self.ui.IP_B.text() + '/' + self.ui.Mask_B.text()
			a = ipaddress.ip_network(ipA, False)
			b = ipaddress.ip_network(ipB, False)
			if (b.subnet_of(a)) == True:
				self.ui.QuickResultsList.addItem('Network: {} is inside Network: {}'.format(str(ipB),str(ipA)))
			else:
				self.ui.QuickResultsList.addItem('Network: {} is NOT inside Network: {}'.format(str(ipB),str(ipA)))
		except:
			messagebox('Error', 'Insert valid IPs first!')
		
	def Host_Subnets_Numbers(self):
		try:
			ip_mask = self.ui.IP_A.text() + '/' + self.ui.Mask_A.text()
			ip_mask = str(ip_mask)
			Nets = IPv4Network(ip_mask, False)
			self.ui.QuickResultsList.addItem('1.Num of Addresses = {} (2 adds for NW/BC)'.format(str(int(Nets.num_addresses) - 2)))
			self.ui.QuickResultsList.addItem('2.Num of Networks = {}'.format(str(2**int(self.ui.Mask_A.text()))))
		except:
			messagebox('Error', 'Insert a valid IP first!')
		
	def Get_BroadcastAndNetworkIPs(self):
		try:
			ip_mask = self.ui.IP_A.text() + '/' + self.ui.Mask_A.text()
			ip_mask = str(ip_mask)
			Nets = IPv4Network(ip_mask, False)
			self.ui.QuickResultsList.addItem('NetworkID: {} & Broadcasting IP: {}'.format(str(Nets.network_address),str(Nets.broadcast_address)))
		except:
			messagebox('Error', 'Insert a valid IP first!')
		
	def Special_IP(self):
		try:
			self.ui.QuickResultsList.addItem(self.ui.IP_A.text()+" is "+IPAddress(self.ui.IP_A.text()))
		except:
			messagebox('Error', 'Insert a valid IP first!')
	def GetMask(self):
		try:
			ip_mask = self.ui.IP_A.text() + '/' + self.ui.Mask_A.text()
			ip_mask = str(ip_mask)
			interface = IPv4Interface(ip_mask)
			Nets = IPv4Network(ip_mask,False)
			self.ui.QuickResultsList.addItem(str(interface.with_netmask) + ' -> ' + str(Nets.netmask))
		except:
			messagebox('Error', 'Insert valid a IP first!')

	def Chnage_Bin_Dec(self):
		try:
			# b = {'0','1'}
			# FirstIPoctet = (self.ui.IP_A.text()).split('.')
			# t = set(FirstIPoctet[0])
			# if b == t or t == {'0'} or t == {'1'}:
			# 	#Decimal
			# 	#Remove Dots First & convert to string after conversion
			# 	BinaryIP_withoutDots = (self.ui.IP_A.text()).replace('.', ' ')
			# 	tempIP = MyIPv4.from_binary_repr(BinaryIP_withoutDots)
			# 	self.ui.QuickResultsList.addItem(str(tempIP))
			# else:
				#Binary
				self.ui.QuickResultsList.addItem(MyIPv4(self.ui.IP_A.text()).binary_repr)
		except:
			messagebox('Error', 'Check your Entries')
			
	def CheckMask(self, IP_text,Masktxt, ID): # ID: 1= IP, 2=IP_A, 3=IP_B
		MaskID = IP_text.split('.')
		if (len(IP_text) > 3): ##First Octet of IP (Decimal!)
			if ID == 1:
				print(Masktxt)
				if int(MaskID[0]) >= 0 and int(MaskID[0]) <= 127 and len(Masktxt) == 0:self.ui.Mask.setText('8')
				elif int(MaskID[0]) >= 128 and int(MaskID[0]) <= 191 and len(Masktxt) == 0:self.ui.Mask.setText('16')
				elif int(MaskID[0]) >= 192 and int(MaskID[0]) <= 223 and len(Masktxt) == 0:self.ui.Mask.setText('24')

				if int(MaskID[0]) >= 0 and int(MaskID[0]) <= 127:self.ui.MaskLabel.setText('A')
				if int(MaskID[0]) >= 128 and int(MaskID[0]) <= 191:self.ui.MaskLabel.setText('B')
				if int(MaskID[0]) >= 192 and int(MaskID[0]) <= 223:self.ui.MaskLabel.setText('C')

			elif ID ==2 and len(Masktxt) == 0:
				if int(MaskID[0]) >= 0 and int(MaskID[0]) <= 127:self.ui.Mask_A.setText('8')
				elif int(MaskID[0]) >= 128 and int(MaskID[0]) <= 191:self.ui.Mask_A.setText('16')
				elif int(MaskID[0]) >= 192 and int(MaskID[0]) <= 223:self.ui.Mask_A.setText('24')
			elif ID ==3 and len(Masktxt) == 0:
				if int(MaskID[0]) >= 0 and int(MaskID[0]) <= 127:self.ui.Mask_B.setText('8')
				elif int(MaskID[0]) >= 128 and int(MaskID[0]) <= 191:self.ui.Mask_B.setText('16')
				elif int(MaskID[0]) >= 192 and int(MaskID[0]) <= 223:self.ui.Mask_B.setText('24')

if __name__ == '__main__':
	app = QApplication(sys.argv)
	w = MyForm()
	w.show()
	sys.exit(app.exec_())