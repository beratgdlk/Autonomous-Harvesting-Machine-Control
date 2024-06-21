from tkinter import *
from time import sleep
from copy import deepcopy                           # kopyalama yaparken oluşan teknik bir detaydan dolayı

from pathfinding.core.grid import Grid              # oluşturduğumuz mapi verip bize kendince bir kareli sistem yaratan fonksiyon
from pathfinding.finder.a_star import AStarFinder   # Arama algoritmamız olan a*


class World:                                        # Dünya diye nitelendirdiğimiz obje, nerdeyse her şeyi içine yerleştirdik
    def __init__(self, root, map):                  # Yaratıcı fonksiyon. root -> Tkinterin sunduğu pencere, map -> Yer şeklimiz
        self.crops = [                              # Elimizdeki ekin çeşitleri
            'Tomato',
            'Carrot',
            'Eggplant',
            'Spinach'
        ]
        self.block_size = 50                        # Her bir karenin standart ölçüsü olması için
        self.grid = map                             # Dünyanın görünüşü, içine 10x10 luk bir matris veriyoruz
        self.active = StringVar(root, 'Tomato')     # Menüde seçili olan ekini aklında tutan değişken
        self.canvas = Canvas(root, height=500, width=500, bg='lightgreen')      # Çizimleri yapacağımız genel kanvas
        self.vehicle = Vehicle()                    # Aracımızı, dünyanın bir niteliği olarak iliştiriyoruz. Bu satır Vehicle classındaki yaratıcı fonksiyonu çalıştıracak
        self.checks = []                            # Toplanması için seçilen ekin listesi

        self.canvas.bind('<Configure>', self.createGrid)        # Dünya yaratılınca ilk olarak createGrid methodunun çalışmasını istiyoruz. Bu kareli parçalara ayıracak.
        self.canvas.bind('<ButtonPress-1>', self.leftClick)     # Sol clicke basıldığında çalışacak method -> leftClick

        drop = OptionMenu(root, self.active, *self.crops)       # Ekin tipi seçilmesi için bir Tkinter Widget'i. İlk argüman: içinde bulunacağı pencere, ikinci: seçilen nesneyi tutar, üçüncü: görülebilecek ekinler listesi
        button = Button(root, text="Harvest", command=self.harvest, font=('ariel', 16))     # Tıklanıldığında toplama işlemini başlatan düğme. Basıldığında harvest methodu çalışır
        
        CheckVar1 = StringVar()                                                                                    # Tkinterin değişkenleri kontrol etmeyi kolaylaştıran
        CheckVar2 = StringVar()                                                                                    # tipleri. String ve StringVar aslında aynı gibi olsalar da
        CheckVar3 = StringVar()                                                                                    # menüden seçilen ekini hatırlamak, dinamik olarak textleri
        CheckVar4 = StringVar()                                                                                    # değiştirmek gibi şeyleri yapabilmemiz için olması gereken
        self.checks = [CheckVar1, CheckVar2, CheckVar3, CheckVar4]                                                 # yöntem

        check1 = Checkbutton(root, text=self.crops[0], variable=CheckVar1, onvalue=self.crops[0], offvalue='')     # Toplanması için tikleyebileceğimiz seçenekler.
        check2 = Checkbutton(root, text=self.crops[1], variable=CheckVar2, onvalue=self.crops[1], offvalue='')     # text -> üzerinde yazması istenen, variable -> seçeneği
        check3 = Checkbutton(root, text=self.crops[2], variable=CheckVar3, onvalue=self.crops[2], offvalue='')     # akılda tutmaya yarar. onvalue ve offvalue ise tikli veya
        check4 = Checkbutton(root, text=self.crops[3], variable=CheckVar4, onvalue=self.crops[3], offvalue='')     # tiksizken almasını istediğimiz değerler. Yani harvest butonuna bastığımızda seçili olan tikler isimlerini harveste yollayacak.
        
        self.canvas.grid(row=0, column=0, rowspan=4)           #    Üstte yaratılan widgetleri (buton, menü, tik kutusu) konumlandırmak için yapılan ayarlar.
        drop.grid(row=0, column=1, columnspan=2, sticky='S')   #    Akışla alakası yok sadece x y axislerinde konumlandırmak için.
        check1.grid(row=1, column=1)                           #
        check2.grid(row=1, column=2)                           #
        check3.grid(row=2, column=1)                           #
        check4.grid(row=2, column=2)                           #
        button.grid(row=3, column=1, columnspan=2)             #

        root.grid_columnconfigure(0, weight=6)                 #
        root.grid_columnconfigure(1, weight=1)                 #
        root.grid_columnconfigure(2, weight=1)                 #
        root.grid_rowconfigure(0, weight=5)                    #
        root.grid_rowconfigure(1, weight=1)                    #
        root.grid_rowconfigure(2, weight=1)                    #
        root.grid_rowconfigure(3, weight=5)                    #

    def createGrid(self, event=None):                   # Dünya yaratıldığında çalışır. 10x10 bir dünya yaratır.
        for y in range(0, 10):
            for x in range(0, 10):
                x1 = (x * self.block_size)
                x2 = (x1 + self.block_size)
                y1 = (y * self.block_size)
                y2 = (y1 + self.block_size)

                self.canvas.create_rectangle(x1,y1,x2,y2, fill='lightgray')     #x1y1 sol üst nokta iken x2y2 sağ alt nokta. Yani her bir nokta için koordinat hesabı

        self.canvas.update()        # Kareler çizildikten sonra ekrana yansıması için update ediyoruz canvası

    def findPath(self, ex, ey):                 # parametreler ex ve ey. Yani End x,y. Gidilecek kareye olan yolu hesaplar.
        [sx, sy] = self.vehicle.coordinate      # aracın koordinatlarını, yani algoritmaya başlangıç koordinatlarını alıyorz

        copy = deepcopy(self.grid)              # Bu yapılmasaydı orjinal mapte değişiklikler yapılacaktı ama bu değişiklikleri geçici olarak yapmamız gerekiyordu, bu yüzden kullandık

        for i in range(0, len(copy)):
            for j in range(0, len(copy)):
                if [j, i] == [ex, ey]:          
                    copy[j][i] = 1              # Gidilecek yeri haritada 1 yaparak ulaşılabilir yap
                    continue

                if copy[j][i] in self.crops:    # Tüm diğer ekinleri ulaşılamaz yap
                    copy[j][i] = 0

        grid = Grid(matrix=copy)                # a star algoritmasını kullanabilmek için grid oluşturuyoruz.
        finder = AStarFinder()                  # arama algoritmasını kullanmak için bir örneğini yarattık
        start = grid.node(sx, sy)               # start başlangıç nodu. Yani arabanın konumu
        end = grid.node(ex, ey)                 # gidilecek nod.

        return finder.find_path(start, end, grid)     # find_path methodu a* algoritmasını kullanır ve gidilecek yolu adım adım geri gönderir.

    def harvest(self):                      # Harvest butonuna basıldığında çalışır
        crops = []                          # Hangi ekinleri toplayacağımız bu listede tutulacak
        for check in self.checks:           # Toplanması için seçilen sebzeler
            if check.get():                 # Tiklenmeyen ekinler boş string olarak geldiği için onları eliyoruz.
                crops.append(check.get())   # Final olarak crops listesinde tiklediğimiz ekin adları yer alırç

        count = 0                           # Tiklenen ekinlerden toplam kaç adet var, bunu tutar.
        for crop in crops:
            for row in self.grid:           # 10x10 dünyaya satır satır bakarak sayar.
                count += row.count(crop)

        for n in range(0, count):              # ekin sayısı kadar toplama işlemi gerçekleşsin istiyoruz                     
            targets = []                       # bu listede gidilebilecek hedefler, yol tarifi ve uzunluğu yer alacak
            for x in range(0, len(self.grid)):                  # Her uygun hedef için yol hesaplayacağız. En sonunda en kısa olanla devam edeceğiz.
                for y in range(0, len(self.grid)):
                    if self.grid[x][y] in crops:                # Mapteki tüm ekinlere bakılır. Eğer tiklenener listesinde iseler devam edilir.
                        path, distance = self.findPath(x, y)    # path: yol tarifi. Distance: uzaklık
                        targets.append([path, distance])        # listeye ekle

            target = sorted(targets, key=lambda x: x[1])[0]     # sorted methodu, ikinci argüman olarak verdiğimiz kurala göre sıralar. Yani uzaklığa göre sıraladık.[0] diyerek ilk elemanı yani en yakınını aldık

            for x, y in target[0]:          # target[0] serisinde en kısa hedefe giden yol adım adım yazıyor. Her bir adımı takip edeceğiz.
                sleep(0.1)                  # Anlık olarak bitmesin diye oyalama methodu.
                self.advance(x*50, y*50)    # Aracı verilen koordinatlara ilerletir.
            
            self.grid[x][y] = 1             # Ulaşıştıktan sonra mapte orayı temizler ve üzerinden geçilebilir yapar.

            self.canvas.itemconfigure(10*y+x+1, fill='lightgray') # Toplanan ekinin olduğu kareyi tekrar default renge getirdik.
            self.canvas.update()                                  # Değişikliklerin görülmesi için canvası güncelle

    def leftClick(self, event):                                 # Haritaya tıkladığımızda ekme işlemini yapacak
        item = self.canvas.find_closest(event.x, event.y)[0]    # event objesi tıklamamızla alakalı bilgiler taşır. event.x ve event.y tıkladığımız koordinatları verir.[0] diyerek en yakınını alıyoruz
        x = event.x // 50                           # event objesi piksel cinsinden olduğu için, 10x10 düzlemde anlam kazanması için dönüştürme yapıyoruz.
        y = event.y // 50                           # y 78 ise artık 1'e eşit olacak. İki // işareti böldükten sonra virgülden sonrasını at demek.

        if self.active.get() == self.grid[x][y]:    # yukarıda bahsedilen StringVar tiplerinin değerini okumak için .get() diyoruz. Eğer tıklanan yer seçili ekinle aynı ise
            self.grid[x][y] = 1                     # Tekrar geçilebilir yap çünkü iki kere tıklamayı temizlemek olarak algılıyoruz.
            color ='lightgray'                      # Default yol rengi
        elif self.active.get() == 'Tomato':         # eğer seçili ekin domates ise mapte 1 olan yeri Tomato yap.
            self.grid[x][y] = 'Tomato'              
            color = 'red'                           # Karenin olmasını istediğmiz renk. Aşağısı ile aynı
        elif self.active.get() == 'Carrot':
            self.grid[x][y] = 'Carrot'
            color = 'orange'
        elif self.active.get() == 'Eggplant':
            self.grid[x][y] = 'Eggplant'
            color = 'purple'
        elif self.active.get() == 'Spinach':
            self.grid[x][y] = 'Spinach'
            color = 'green'

        self.canvas.itemconfigure(item, fill=color) # Tıklanan karenin rengini değiştir

    def advance(self, x, y):                            # alınan x, y koordinatlarına ilerler
        self.vehicle.coordinate = [x//50, y//50]           # aracın yeni koordinatları. piksel cinsinden 0-9 arasına scale ediyoruz.
        self.canvas.delete(self.vehicle.square)              # aracın eski konumunu gui'den sil
        self.vehicle.square = window.canvas.create_rectangle(x, y, x + self.block_size, y + self.block_size, fill='blue')   # aracın yeni konumuna yeni bir dikdörtgen çiz
        self.canvas.update()


class Vehicle:                                      # çok temel bir araç nesnesi. Tek kareden oluşur
    def __init__(self):                             # Yaratıcı fonksyion, argümana ihtiyacı yok
        self.coordinate = [0, 0]                    # Aracın koordinatları
        self.square = ''                            # Aracın canvastaki karesinin id'si.


root = Tk()                                         # Yeni pencere
root.title('Harvest Simulator')                     # Başlık
root.resizable(False, False)                        # Ekranın boyutunu değiştirememek için

map = [                                             # 1 geçilebilir, 0 geçilemez. 0.3 gibi değerler verilebilir. Ekim işlemine göre yapı değişecek.
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

window = World(root, map)                           # Dünya objesi yarat. Argümanlar çalışacak pencere ve dünya şekli

root.mainloop()