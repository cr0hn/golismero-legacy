var vulnerabilitiesData = [
    {
        "id": 0,
        "target": "terra.es",
        "criticality": 3,
        "vulnerability": "SQLI"
    },
    {
        "id": 1,
        "target": "terra.es",
        "criticality": 4,
        "vulnerability": "Other"
    },
    {
        "id": 2,
        "target": "deportes.terra.es",
        "criticality": 5,
        "vulnerability": "XSS"
    },
    {
        "id": 3,
        "target": "juegos.terra.es",
        "criticality": 5,
        "vulnerability": "XSS"
    },
    {
        "id": 4,
        "target": "juegos.terra.es",
        "criticality": 1,
        "vulnerability": "XSS"
    },
    {
        "id": 5,
        "target": "terra.es",
        "criticality": 2,
        "vulnerability": "SQLI"
    },
    {
        "id": 6,
        "target": "deportes.terra.es",
        "criticality": 4,
        "vulnerability": "XSS"
    },
    {
        "id": 7,
        "target": "terra.es",
        "criticality": 3,
        "vulnerability": "SQLI"
    },
    {
        "id": 8,
        "target": "deportes.terra.es",
        "criticality": 3,
        "vulnerability": "SQLI"
    },
    {
        "id": 9,
        "target": "deportes.terra.es",
        "criticality": 2,
        "vulnerability": "Other"
    },
    {
        "id": 10,
        "target": "deportes.terra.es",
        "criticality": 4,
        "vulnerability": "Other"
    },
    {
        "id": 11,
        "target": "juegos.terra.es",
        "criticality": 1,
        "vulnerability": "Other"
    },
    {
        "id": 12,
        "target": "juegos.terra.es",
        "criticality": 2,
        "vulnerability": "XSS"
    },
    {
        "id": 13,
        "target": "juegos.terra.es",
        "criticality": 3,
        "vulnerability": "Other"
    },
    {
        "id": 14,
        "target": "deportes.terra.es",
        "criticality": 4,
        "vulnerability": "SQLI"
    },
    {
        "id": 15,
        "target": "juegos.terra.es",
        "criticality": 4,
        "vulnerability": "XSS"
    },
    {
        "id": 16,
        "target": "deportes.terra.es",
        "criticality": 2,
        "vulnerability": "SQLI"
    },
    {
        "id": 17,
        "target": "terra.es",
        "criticality": 5,
        "vulnerability": "XSS"
    },
    {
        "id": 18,
        "target": "deportes.terra.es",
        "criticality": 1,
        "vulnerability": "SQLI"
    },
    {
        "id": 19,
        "target": "deportes.terra.es",
        "criticality": 4,
        "vulnerability": "SQLI"
    },
    {
        "id": 20,
        "target": "terra.es",
        "criticality": 1,
        "vulnerability": "XSS"
    },
    {
        "id": 21,
        "target": "deportes.terra.es",
        "criticality": 3,
        "vulnerability": "Other"
    },
    {
        "id": 22,
        "target": "terra.es",
        "criticality": 4,
        "vulnerability": "Other"
    },
    {
        "id": 23,
        "target": "deportes.terra.es",
        "criticality": 1,
        "vulnerability": "SQLI"
    },
    {
        "id": 24,
        "target": "terra.es",
        "criticality": 1,
        "vulnerability": "XSS"
    },
    {
        "id": 25,
        "target": "juegos.terra.es",
        "criticality": 4,
        "vulnerability": "XSS"
    },
    {
        "id": 26,
        "target": "juegos.terra.es",
        "criticality": 5,
        "vulnerability": "XSS"
    },
    {
        "id": 27,
        "target": "terra.es",
        "criticality": 4,
        "vulnerability": "XSS"
    },
    {
        "id": 28,
        "target": "juegos.terra.es",
        "criticality": 5,
        "vulnerability": "SQLI"
    },
    {
        "id": 29,
        "target": "deportes.terra.es",
        "criticality": 3,
        "vulnerability": "XSS"
    },
    {
        "id": 30,
        "target": "terra.es",
        "criticality": 2,
        "vulnerability": "SQLI"
    }
];


var tecnicalData =[
    {
        "id": 0,
        "target": "deportes.terra.es",
        "resource": [
            {
                "type": "url",
                "vulnerabilities": [
                    {
                        "id": 0,
                        "type": "Other",
                        "level": 1,
                        "language":"python",
                        "code":"print 'Hello, world!'",
                        "description": "Elit proident eiusmod deserunt ut officia duis magna Lorem ex culpa anim eiusmod. In deserunt exercitation ullamco proident magna dolore nostrud duis velit dolor duis sint fugiat magna. Sunt enim et commodo deserunt adipisicing ut consequat duis dolore occaecat cupidatat.\r\n"
                    },
                    {
                        "id": 1,
                        "type": "SQLi",
                        "level": 5,
                        "language":"http",
                        "code":"POST /api/login/token/ HTTP/1.1\r\nHost: golismero.mysite.com\r\nAccept: */*\r\nContent-Length: 29\r\nContent-Type: application/x-www-form-urlencoded\r\n{username=myuser&password=mypassword}",
                        "description": "Laboris ad ut magna labore enim consequat voluptate reprehenderit reprehenderit. Duis commodo ipsum commodo minim ipsum id id est pariatur cupidatat ad. Nulla laborum excepteur est sint duis elit amet aliqua. Pariatur in quis laboris proident minim sunt. Minim labore culpa est ex est enim id laborum quis qui. Sit magna id sint incididunt do ullamco do laborum. Ea est incididunt est culpa nostrud non consequat labore.\r\n"
                    },
                    {
                        "id": 2,
                        "type": "SQLi",
                        "level": 1,
                        "description": "Do magna fugiat sit aliquip eiusmod. Nisi et amet sunt minim ad qui est irure eiusmod ea nisi. Velit anim amet ut magna sit proident labore adipisicing aliqua irure. Lorem sit ut enim tempor est commodo officia enim. In consequat do quis anim id veniam cupidatat incididunt culpa. Irure anim cupidatat commodo ut nostrud et Lorem ea pariatur fugiat. Mollit est ex aliqua veniam nostrud sunt aliquip esse voluptate nulla non nostrud amet.\r\n"
                    },
                    {
                        "id": 3,
                        "type": "XSS",
                        "level": 5,
                        "description": "Adipisicing labore officia Lorem pariatur minim amet officia ipsum. Ipsum labore ullamco voluptate do aute ipsum sit fugiat. Excepteur non culpa cillum nostrud. Exercitation laboris non labore sunt consequat ad laborum duis ullamco cupidatat ipsum. Qui aute dolore id amet pariatur exercitation ut aliquip pariatur nulla.\r\n"
                    },
                    {
                        "id": 4,
                        "type": "SQLi",
                        "level": 3,
                        "description": "Qui sunt ipsum pariatur occaecat laboris proident. Anim commodo irure ad adipisicing commodo commodo labore cillum nostrud eiusmod excepteur. Officia sint nulla Lorem aliqua. Velit aliquip anim voluptate aliquip magna ex consequat fugiat. Tempor id ipsum mollit adipisicing ex duis do dolor dolor. In officia fugiat laborum amet exercitation esse consequat labore elit aute qui qui exercitation. Ullamco consequat aliqua voluptate labore magna culpa et tempor dolor et dolor veniam.\r\n"
                    }
                ]
            },
            {
                "type": "domain",
                "vulnerabilities": [
                    {
                        "id": 0,
                        "type": "SQLi",
                        "level": 2,
                        "description": "In eiusmod proident quis voluptate occaecat enim eiusmod magna sit sint minim dolore eu culpa. Incididunt amet consequat voluptate fugiat tempor dolor occaecat elit eiusmod incididunt irure pariatur voluptate. Quis ad consectetur proident aliquip nostrud consectetur tempor veniam ullamco eu. Sunt est ullamco sit ut. Eu ex et voluptate sint. Do exercitation do non pariatur quis eiusmod.\r\n"
                    },
                    {
                        "id": 1,
                        "type": "Other",
                        "level": 5,
                        "description": "Esse velit duis veniam sint ex dolore officia ullamco id. Pariatur ullamco laborum non est consectetur ad ex occaecat. Aliqua eu esse et aliquip.\r\n"
                    },
                    {
                        "id": 2,
                        "type": "XSS",
                        "level": 1,
                        "description": "Laborum sint ea officia aute aliquip reprehenderit veniam duis qui magna eu sint. Laboris sit minim in quis mollit amet. Consectetur dolor cupidatat labore voluptate veniam enim ullamco cupidatat ea commodo dolor. Eiusmod est dolore cillum qui Lorem.\r\n"
                    },
                    {
                        "id": 3,
                        "type": "SQLi",
                        "level": 2,
                        "description": "Est qui ipsum cillum ipsum non velit ut amet reprehenderit labore. Velit aliqua in irure et anim consequat laboris cillum. Id ad Lorem ipsum velit duis excepteur dolor id Lorem. Do enim tempor exercitation et.\r\n"
                    },
                    {
                        "id": 4,
                        "type": "Other",
                        "level": 5,
                        "description": "Tempor aliquip et pariatur eiusmod. Minim anim tempor minim velit adipisicing non consectetur laborum ex nisi adipisicing ullamco labore eiusmod. Dolor aliqua nisi eu esse in sunt.\r\n"
                    },
                    {
                        "id": 5,
                        "type": "SQLi",
                        "level": 6,
                        "description": "Eiusmod irure labore duis commodo sint aliquip dolor. Est est ullamco eu non dolore anim qui fugiat esse aliquip ut duis exercitation nulla. Cupidatat proident commodo et do duis consectetur pariatur fugiat labore. Eu eiusmod laboris tempor commodo.\r\n"
                    }
                ]
            },
            {
                "type": "ip",
                "vulnerabilities": [
                    {
                        "id": 0,
                        "type": "Other",
                        "level": 2,
                        "description": "Duis aliquip proident fugiat veniam labore veniam anim cupidatat. Enim labore mollit magna qui veniam magna non cillum Lorem commodo in exercitation mollit. Dolor exercitation sint dolor mollit officia quis. Id elit fugiat est aliquip pariatur non voluptate consequat in ipsum magna ea. Ipsum aliqua enim ut culpa sint duis reprehenderit ea laboris amet. Id excepteur in eu elit consectetur enim sit. Do aute cillum do fugiat nostrud pariatur sint sint cupidatat eu incididunt.\r\n"
                    },
                    {
                        "id": 1,
                        "type": "Other",
                        "level": 3,
                        "description": "Elit dolor mollit velit fugiat aliquip ex. Cillum reprehenderit ipsum aute veniam laborum. Ullamco ipsum do velit quis est sit laborum voluptate qui consequat. Exercitation culpa qui quis tempor est.\r\n"
                    },
                    {
                        "id": 2,
                        "type": "Other",
                        "level": 6,
                        "description": "Incididunt laborum consequat minim consectetur dolore velit cillum do qui ex officia. Officia dolor veniam pariatur Lorem Lorem veniam pariatur pariatur ea occaecat fugiat duis est aliquip. Aute anim aliquip est est.\r\n"
                    },
                    {
                        "id": 3,
                        "type": "SQLi",
                        "level": 2,
                        "description": "Nisi excepteur veniam Lorem veniam consequat ea aute cillum sint cupidatat velit aute. Minim aliquip do nisi ex mollit elit. Fugiat ullamco nisi do qui occaecat proident cupidatat quis minim velit culpa consequat consequat.\r\n"
                    },
                    {
                        "id": 4,
                        "type": "XSS",
                        "level": 2,
                        "description": "Enim nulla in ea occaecat occaecat ad non cillum proident dolore ipsum. Ea laboris deserunt fugiat nisi Lorem id sint. Ipsum nulla esse anim et proident. In do nulla id amet amet aliqua incididunt ullamco et. Enim exercitation eu proident proident voluptate veniam consequat qui ea cupidatat incididunt ex proident sunt. Quis ipsum laboris anim anim ea qui ullamco ut nulla adipisicing Lorem tempor sit.\r\n"
                    },
                    {
                        "id": 5,
                        "type": "XSS",
                        "level": 5,
                        "description": "Non mollit duis pariatur occaecat. Reprehenderit ea adipisicing consectetur sunt amet officia laboris anim ullamco esse qui et aute. Consectetur fugiat laborum ipsum ipsum deserunt voluptate magna qui et sunt aute nostrud.\r\n"
                    },
                    {
                        "id": 6,
                        "type": "SQLi",
                        "level": 5,
                        "description": "Ipsum consequat dolor aliqua consequat exercitation officia magna mollit dolore veniam sit proident tempor consectetur. Aute fugiat cillum velit ullamco officia incididunt do consectetur. Ipsum laboris excepteur esse dolore exercitation exercitation sint elit qui. Lorem minim cillum laboris incididunt exercitation quis esse laboris occaecat commodo veniam ipsum minim. Deserunt Lorem ipsum voluptate non exercitation. Aliquip duis culpa anim aute tempor consectetur mollit laborum voluptate consectetur anim. Eu deserunt reprehenderit excepteur duis veniam consectetur tempor dolor fugiat.\r\n"
                    },
                    {
                        "id": 7,
                        "type": "XSS",
                        "level": 2,
                        "description": "Elit enim irure ullamco nisi irure sint labore sint dolor. Est veniam voluptate id minim excepteur voluptate labore tempor excepteur et. Fugiat deserunt non magna sunt nisi. Irure pariatur qui pariatur amet enim tempor proident qui est nulla aliqua nulla. Ipsum qui ex cupidatat nisi qui irure labore.\r\n"
                    },
                    {
                        "id": 8,
                        "type": "XSS",
                        "level": 5,
                        "description": "Sunt et est excepteur ea consequat non laboris consequat incididunt in nostrud laboris sunt. Magna laboris exercitation cillum cupidatat sit et irure mollit non. Culpa qui est nisi fugiat ut sunt nostrud sit anim.\r\n"
                    },
                    {
                        "id": 9,
                        "type": "XSS",
                        "level": 5,
                        "description": "Officia Lorem minim sit exercitation tempor fugiat deserunt nulla mollit et minim ullamco officia cillum. Laboris nisi non proident adipisicing eu Lorem ut in Lorem incididunt adipisicing. Nulla eiusmod ad dolore reprehenderit adipisicing dolor quis consequat elit incididunt. Dolore ut incididunt ex duis id consequat nulla amet tempor non eiusmod dolor nisi consequat. Voluptate proident sint proident cillum qui eu.\r\n"
                    }
                ]
            },
            {
                "type": "email",
                "vulnerabilities": [
                    {
                        "id": 0,
                        "type": "Other",
                        "level": 5,
                        "description": "Commodo officia qui Lorem eiusmod. Veniam anim est aliquip deserunt esse. Eiusmod minim ea voluptate sit est dolore consectetur ullamco. Sint anim consequat incididunt enim eiusmod sint enim qui id adipisicing culpa laboris.\r\n"
                    },
                    {
                        "id": 1,
                        "type": "SQLi",
                        "level": 6,
                        "description": "Consectetur nostrud dolor fugiat commodo minim reprehenderit. Magna et pariatur reprehenderit do laboris voluptate cillum ea qui. Mollit ea voluptate velit proident labore esse in eiusmod sit non minim in cupidatat enim. Sunt aliquip officia adipisicing dolor. Laboris non commodo laboris ad irure voluptate.\r\n"
                    },
                    {
                        "id": 2,
                        "type": "SQLi",
                        "level": 2,
                        "description": "Labore magna laboris commodo veniam ut eiusmod veniam eu. Aute consectetur consequat mollit officia ut enim in. Aliqua pariatur ex quis proident est ut amet voluptate aliquip.\r\n"
                    },
                    {
                        "id": 3,
                        "type": "XSS",
                        "level": 4,
                        "description": "Aliqua fugiat magna exercitation mollit aute labore do aute ex eu proident. Eu deserunt in ut non veniam id eiusmod laborum pariatur magna veniam. Elit elit ad nostrud consectetur labore eiusmod pariatur dolor ex veniam aliquip.\r\n"
                    },
                    {
                        "id": 4,
                        "type": "SQLi",
                        "level": 1,
                        "description": "Ut non tempor ipsum culpa non ipsum esse ullamco. Commodo enim enim ex in. Do do id exercitation et laboris mollit adipisicing in sit aliquip mollit incididunt ad laborum.\r\n"
                    },
                    {
                        "id": 5,
                        "type": "SQLi",
                        "level": 4,
                        "description": "Nulla id proident sit et deserunt est culpa Lorem cillum do aliquip incididunt cupidatat mollit. Ea qui quis id minim. Quis mollit id veniam aliqua consectetur voluptate velit aliqua est. Magna occaecat cillum occaecat adipisicing elit enim. Nostrud est tempor voluptate dolore laborum id irure irure nulla. Cillum commodo minim minim sunt adipisicing proident sit consectetur sint elit mollit in.\r\n"
                    },
                    {
                        "id": 6,
                        "type": "Other",
                        "level": 6,
                        "description": "Eu eiusmod enim dolor amet eiusmod aute ea officia ipsum officia occaecat. Dolore aute laboris dolor consectetur enim Lorem do irure deserunt aliquip occaecat eiusmod eu. Culpa eu nostrud do excepteur laborum Lorem dolor excepteur adipisicing elit aute eu cupidatat. Nostrud ad mollit id ea cupidatat ea exercitation ipsum sint cupidatat tempor laborum. Consequat tempor ut cupidatat voluptate ut. Aliqua duis commodo consequat ut eiusmod do. Officia sunt deserunt veniam amet qui veniam.\r\n"
                    }
                ]
            }
        ]
    },
    {
        "id": 1,
        "target": "terra.es",
        "resource": [
            {
                "type": "url",
                "vulnerabilities": [
                    {
                        "id": 0,
                        "type": "Other",
                        "level": 5,
                        "description": "Id duis anim ipsum ullamco consequat esse. Est nisi minim eu commodo reprehenderit ad. Qui veniam reprehenderit nulla labore aliquip do. Eu est aliquip nulla ad eu.\r\n"
                    },
                    {
                        "id": 1,
                        "type": "Other",
                        "level": 6,
                        "description": "Culpa culpa excepteur ad dolor ad ad adipisicing sit. Proident voluptate id voluptate dolor excepteur exercitation qui esse reprehenderit aute duis Lorem sit laboris. Sit nulla voluptate aliquip ullamco excepteur tempor excepteur ullamco qui. Veniam ut qui laboris ut enim laboris. Commodo minim mollit exercitation duis laboris. Proident non id et mollit sint culpa aliquip fugiat sint.\r\n"
                    },
                    {
                        "id": 2,
                        "type": "XSS",
                        "level": 6,
                        "description": "Cupidatat enim aliquip laboris irure do quis culpa voluptate proident magna ipsum Lorem. Pariatur aliquip ullamco do elit sunt nulla consequat. Quis commodo ut pariatur reprehenderit excepteur sunt. Deserunt fugiat incididunt laboris labore elit cupidatat non nisi laboris pariatur. Deserunt aliqua tempor esse do. Dolore nulla consequat esse ad reprehenderit aliqua aute.\r\n"
                    },
                    {
                        "id": 3,
                        "type": "Other",
                        "level": 1,
                        "description": "Ullamco eiusmod eu esse nulla sunt ea voluptate sint occaecat ullamco Lorem fugiat ullamco. Occaecat quis adipisicing sunt ullamco ad minim. In esse adipisicing magna do aliquip nulla non nulla aliquip Lorem anim est et. Veniam sunt Lorem nulla consectetur officia ullamco id incididunt fugiat mollit cillum aute.\r\n"
                    },
                    {
                        "id": 4,
                        "type": "SQLi",
                        "level": 2,
                        "description": "Id elit duis consectetur officia proident laboris nisi do. Mollit voluptate nulla voluptate reprehenderit aliquip dolor mollit aliquip proident nostrud reprehenderit consequat. Cillum proident aute laborum consequat pariatur minim et reprehenderit dolor. Eu mollit mollit est eu. Irure qui aliquip anim sint amet Lorem eiusmod dolore sit.\r\n"
                    }
                ]
            },
            {
                "type": "domain",
                "vulnerabilities": [
                    {
                        "id": 0,
                        "type": "Other",
                        "level": 6,
                        "description": "Enim aute duis enim consequat enim commodo ad fugiat esse pariatur cillum exercitation. Dolor laborum exercitation dolor labore reprehenderit ea velit magna veniam velit. Ea aute labore officia aute velit dolore aliquip anim in consequat qui dolore irure officia. Sint veniam incididunt amet occaecat non anim deserunt ut minim reprehenderit deserunt fugiat anim ex.\r\n"
                    },
                    {
                        "id": 1,
                        "type": "Other",
                        "level": 4,
                        "description": "Dolore magna non exercitation velit sit duis consectetur eiusmod mollit. Irure excepteur mollit Lorem dolor mollit. Eu est dolore occaecat consectetur enim ad aliquip qui aliqua aute.\r\n"
                    },
                    {
                        "id": 2,
                        "type": "Other",
                        "level": 6,
                        "description": "Velit duis sunt pariatur fugiat amet laborum. Commodo ex dolor minim officia laborum ea do adipisicing eiusmod. Duis cupidatat ipsum cupidatat aute cupidatat dolor incididunt incididunt. Quis ea id velit do aute culpa duis. Officia do aliqua laborum anim dolor amet magna.\r\n"
                    },
                    {
                        "id": 3,
                        "type": "Other",
                        "level": 3,
                        "description": "Laborum pariatur sit aliqua ut reprehenderit adipisicing est aliquip sunt incididunt Lorem eiusmod aliquip sit. Dolor dolore nisi enim do tempor dolor qui non ut et aute minim dolore. Non amet est eiusmod do pariatur elit qui labore eu ea veniam. Deserunt aliqua officia voluptate deserunt aute occaecat. Aliqua cupidatat laboris non duis consectetur laboris. Ad pariatur fugiat cupidatat laboris enim officia eu dolor sit id nisi ut consectetur. Adipisicing est dolor veniam minim ex.\r\n"
                    },
                    {
                        "id": 4,
                        "type": "XSS",
                        "level": 4,
                        "description": "Adipisicing nulla qui tempor enim adipisicing esse incididunt ex adipisicing incididunt amet. Eu magna cillum exercitation cupidatat laboris proident elit commodo laboris sunt exercitation nulla. Aliqua consectetur nisi occaecat dolor esse.\r\n"
                    },
                    {
                        "id": 5,
                        "type": "SQLi",
                        "level": 5,
                        "description": "Consectetur reprehenderit consectetur nostrud fugiat veniam excepteur proident nostrud veniam nulla fugiat et. Nulla dolor esse adipisicing in non. Enim ex ea sit eu in incididunt sunt non dolore labore fugiat est amet nulla. Nulla id commodo culpa aliquip veniam nulla duis veniam qui occaecat. Consectetur adipisicing ex esse excepteur Lorem labore nisi exercitation anim. Sint excepteur sit sunt nulla eiusmod culpa.\r\n"
                    },
                    {
                        "id": 6,
                        "type": "SQLi",
                        "level": 6,
                        "description": "Mollit sunt esse ea culpa Lorem sit id. Est nostrud ut qui aliquip id aliqua culpa aliqua voluptate eu. Incididunt minim consectetur enim excepteur voluptate dolore consequat occaecat duis qui consequat in enim.\r\n"
                    },
                    {
                        "id": 7,
                        "type": "XSS",
                        "level": 1,
                        "description": "Voluptate do consectetur Lorem culpa ut ipsum mollit voluptate culpa tempor sint eiusmod Lorem incididunt. Tempor qui sint consectetur minim exercitation dolore aliqua quis dolor deserunt ullamco. Irure ea minim culpa et. Non nostrud cupidatat cillum cillum aliquip qui. Elit anim nulla veniam adipisicing. Aliqua tempor enim dolor et id et ex veniam voluptate elit cupidatat nostrud.\r\n"
                    },
                    {
                        "id": 8,
                        "type": "XSS",
                        "level": 4,
                        "description": "Minim irure fugiat mollit reprehenderit tempor. Pariatur eu irure officia consectetur et. Officia Lorem incididunt ex proident. Tempor aliquip est aliquip adipisicing. In id excepteur consequat magna.\r\n"
                    },
                    {
                        "id": 9,
                        "type": "Other",
                        "level": 5,
                        "description": "Consequat ea consequat cillum sint commodo et sit ea proident culpa nostrud. Non veniam excepteur reprehenderit dolore magna minim dolore cillum reprehenderit officia Lorem eiusmod sint. Irure veniam velit non velit.\r\n"
                    }
                ]
            },
            {
                "type": "email",
                "vulnerabilities": [
                    {
                        "id": 0,
                        "type": "Other",
                        "level": 6,
                        "description": "Sint ut eiusmod enim elit nulla irure cillum voluptate amet veniam mollit. Occaecat esse laborum veniam dolor irure ut cupidatat commodo laborum consectetur consequat aute laborum incididunt. Amet enim deserunt consequat proident labore duis minim irure aliqua adipisicing in occaecat in ipsum. Proident Lorem veniam dolor pariatur commodo duis laboris consequat occaecat amet. Exercitation commodo aute ullamco fugiat veniam aute voluptate laboris cillum excepteur voluptate.\r\n"
                    },
                    {
                        "id": 1,
                        "type": "Other",
                        "level": 4,
                        "description": "Sunt laboris mollit adipisicing do fugiat. Ex reprehenderit consectetur adipisicing eiusmod. Aliquip ut in eiusmod et sunt aute eiusmod tempor. Eu fugiat esse elit nostrud in enim commodo dolore deserunt voluptate culpa.\r\n"
                    },
                    {
                        "id": 2,
                        "type": "XSS",
                        "level": 1,
                        "description": "Deserunt sint ullamco ex id id non nostrud mollit qui cillum ea labore adipisicing. Elit nostrud ullamco esse veniam culpa cupidatat nisi officia amet proident. Deserunt velit voluptate laboris ipsum mollit non aute irure proident aliqua cupidatat do nostrud.\r\n"
                    },
                    {
                        "id": 3,
                        "type": "XSS",
                        "level": 6,
                        "description": "Esse proident exercitation dolore officia. Velit enim consequat eiusmod voluptate fugiat elit dolor est pariatur eiusmod labore culpa. Reprehenderit consequat esse labore nisi magna consequat. Ea ut amet consectetur ad commodo ex cillum ea laboris pariatur commodo enim. Non tempor qui sit veniam consectetur enim pariatur fugiat non velit ipsum culpa. Sint magna amet ex aliquip cillum aliquip aliqua laborum aliquip adipisicing sunt. Deserunt ullamco adipisicing aliqua laborum mollit eu Lorem labore elit reprehenderit occaecat.\r\n"
                    },
                    {
                        "id": 4,
                        "type": "XSS",
                        "level": 4,
                        "description": "Officia ea sint anim reprehenderit nulla nulla quis minim ad duis sit. Exercitation nostrud officia sit incididunt quis cillum. Proident aute commodo cillum sint nulla sunt est qui esse eu.\r\n"
                    },
                    {
                        "id": 5,
                        "type": "SQLi",
                        "level": 6,
                        "description": "Velit aute adipisicing ut labore laboris labore Lorem eu. Ea esse mollit incididunt eiusmod duis. Dolor nostrud qui adipisicing tempor ad id veniam dolor. Consectetur laborum ut quis sint. Ex voluptate elit et est pariatur elit proident. Esse sit est minim minim velit cupidatat nulla consequat labore.\r\n"
                    }
                ]
            },
            {
                "type": "ip",
                "vulnerabilities": [
                    {
                        "id": 0,
                        "type": "Other",
                        "level": 3,
                        "description": "Exercitation in non exercitation ipsum. Eu est labore nulla do dolore adipisicing voluptate adipisicing consectetur dolor quis magna aliqua anim. Qui minim ex pariatur do ipsum. Dolor enim commodo ea enim sint aute et quis quis pariatur id. Sint anim occaecat in tempor quis ea eiusmod elit velit laboris irure elit ipsum adipisicing. Cupidatat adipisicing id tempor esse eiusmod in.\r\n"
                    },
                    {
                        "id": 1,
                        "type": "SQLi",
                        "level": 2,
                        "description": "In do veniam enim aute duis tempor commodo magna. Quis et enim reprehenderit magna. Minim tempor minim et incididunt consequat minim. Minim magna et aliquip cillum. Officia consectetur exercitation nisi Lorem nulla anim sit minim do cupidatat voluptate. Non aliquip nulla proident minim deserunt deserunt deserunt ea est tempor elit eu. Occaecat minim exercitation et pariatur culpa.\r\n"
                    },
                    {
                        "id": 2,
                        "type": "SQLi",
                        "level": 2,
                        "description": "Deserunt sunt in eu ullamco id. Et deserunt fugiat tempor exercitation ipsum minim ad mollit. Officia quis mollit ullamco reprehenderit sunt voluptate velit duis Lorem voluptate do ut.\r\n"
                    },
                    {
                        "id": 3,
                        "type": "SQLi",
                        "level": 2,
                        "description": "Consectetur velit est Lorem consectetur ex. Sit quis veniam laboris labore laborum cillum. Ut labore eu dolor tempor ut fugiat reprehenderit dolor.\r\n"
                    },
                    {
                        "id": 4,
                        "type": "SQLi",
                        "level": 4,
                        "description": "Cillum enim enim ea et ex laboris incididunt labore pariatur pariatur nulla exercitation quis. Est irure elit est irure cillum ipsum excepteur quis labore laborum voluptate tempor. Voluptate irure laborum labore ea est sit quis incididunt qui et.\r\n"
                    },
                    {
                        "id": 5,
                        "type": "SQLi",
                        "level": 2,
                        "description": "Ipsum consectetur culpa incididunt occaecat anim ea voluptate commodo. Cillum excepteur mollit culpa enim aliqua et qui et culpa eu amet minim deserunt consectetur. Irure nulla duis dolore ullamco reprehenderit anim aute.\r\n"
                    },
                    {
                        "id": 6,
                        "type": "SQLi",
                        "level": 4,
                        "description": "Nostrud culpa do laborum eiusmod Lorem. Aliquip pariatur aliqua velit laboris non nostrud sit commodo sit cillum aute laborum qui sint. Duis quis in anim aliqua nostrud.\r\n"
                    },
                    {
                        "id": 7,
                        "type": "SQLi",
                        "level": 1,
                        "description": "Non consequat ad amet id duis commodo consectetur ipsum pariatur exercitation magna amet exercitation. Pariatur mollit cillum veniam sint pariatur. Magna occaecat et non dolore exercitation nulla nostrud consequat. Commodo cupidatat eiusmod velit ea. Amet laboris do et irure eiusmod id aute.\r\n"
                    }
                ]
            }
        ]
    },
    {
        "id": 2,
        "target": "juegos.terra.es",
        "resource": [
            {
                "type": "email",
                "vulnerabilities": [
                    {
                        "id": 0,
                        "type": "SQLi",
                        "level": 3,
                        "description": "Veniam aute culpa aliquip dolore. Veniam enim in aliquip non. Mollit elit pariatur excepteur officia exercitation eu. Proident laborum excepteur cillum eiusmod Lorem veniam nisi labore cillum qui adipisicing sint. Officia excepteur incididunt qui eu tempor deserunt minim dolore labore in occaecat labore velit.\r\n"
                    },
                    {
                        "id": 1,
                        "type": "XSS",
                        "level": 3,
                        "description": "Commodo eiusmod pariatur et ad velit ullamco tempor. Minim incididunt magna incididunt quis pariatur mollit adipisicing fugiat anim elit eiusmod quis incididunt. Eiusmod quis ea voluptate consectetur consequat. Culpa ad enim dolor commodo culpa dolore adipisicing laboris qui voluptate occaecat. Nostrud amet nulla cillum quis Lorem. Qui pariatur voluptate elit qui consectetur dolor amet. Est ipsum labore incididunt id in ex adipisicing ad sint incididunt elit adipisicing.\r\n"
                    },
                    {
                        "id": 2,
                        "type": "Other",
                        "level": 3,
                        "description": "Dolor incididunt eu qui anim occaecat nulla. Proident exercitation deserunt eiusmod labore occaecat sunt dolor dolore ea. Nisi velit ex culpa magna deserunt nulla non laboris dolor ad excepteur in. Esse Lorem aliquip nisi consequat. Cupidatat ad sint dolore aute cupidatat anim dolor proident dolor minim commodo sunt reprehenderit reprehenderit. Culpa aute sint consequat adipisicing. Ullamco nostrud qui occaecat in fugiat.\r\n"
                    },
                    {
                        "id": 3,
                        "type": "XSS",
                        "level": 1,
                        "description": "Ex quis ea adipisicing eu. Ut incididunt velit commodo eu ut cupidatat quis adipisicing. Aute commodo deserunt magna ex. Nisi adipisicing exercitation laboris voluptate laboris duis anim aliqua.\r\n"
                    },
                    {
                        "id": 4,
                        "type": "Other",
                        "level": 5,
                        "description": "Adipisicing occaecat nulla laboris eu commodo. Reprehenderit in nostrud consequat duis minim fugiat nulla laborum magna. Elit dolor culpa mollit pariatur duis eiusmod mollit.\r\n"
                    },
                    {
                        "id": 5,
                        "type": "SQLi",
                        "level": 6,
                        "description": "Id voluptate magna tempor laborum nulla dolor. Velit quis sunt ullamco officia ipsum sit nulla. Nisi voluptate occaecat ad minim ullamco consectetur sint irure ipsum ex veniam. Do irure proident exercitation eu laboris fugiat exercitation est ipsum.\r\n"
                    }
                ]
            },
            {
                "type": "domain",
                "vulnerabilities": [
                    {
                        "id": 0,
                        "type": "SQLi",
                        "level": 5,
                        "description": "Eiusmod aliqua excepteur anim culpa esse commodo excepteur cupidatat nulla nostrud. Irure eu est irure consectetur culpa esse esse irure incididunt est. Ut ad pariatur aute ullamco exercitation qui eu do exercitation tempor quis commodo dolor. Irure incididunt proident magna culpa occaecat. In consectetur aliquip labore ex reprehenderit ad officia eiusmod consectetur proident nostrud. Excepteur est voluptate labore dolore aute deserunt voluptate. Ipsum occaecat qui occaecat sunt.\r\n"
                    },
                    {
                        "id": 1,
                        "type": "SQLi",
                        "level": 5,
                        "description": "Lorem nulla ad cupidatat ea in enim. Deserunt ullamco fugiat in in eu eu anim est occaecat labore. Sunt nulla tempor voluptate do sunt. Reprehenderit cillum nostrud occaecat et do cillum. Voluptate aute irure tempor est consequat cupidatat. Aute aliquip sint ut Lorem.\r\n"
                    },
                    {
                        "id": 2,
                        "type": "SQLi",
                        "level": 2,
                        "description": "Fugiat aliquip tempor enim duis. Sit Lorem laborum id et adipisicing in ullamco enim ea officia consectetur deserunt laboris. Incididunt ex non dolore tempor ullamco in tempor duis officia cillum non adipisicing nisi irure. Exercitation nisi adipisicing adipisicing veniam proident consequat excepteur adipisicing aliquip pariatur culpa. Eu exercitation aliquip cillum duis cupidatat id et et in.\r\n"
                    },
                    {
                        "id": 3,
                        "type": "SQLi",
                        "level": 1,
                        "description": "Consectetur adipisicing fugiat sit nulla nisi laboris veniam est sint Lorem sit amet culpa. Reprehenderit et laborum est amet reprehenderit reprehenderit minim fugiat do in esse reprehenderit qui. Cillum minim fugiat commodo cupidatat qui est. Duis cillum enim nostrud aliquip esse mollit cillum cillum sit Lorem esse. Enim fugiat dolor adipisicing nulla minim veniam.\r\n"
                    },
                    {
                        "id": 4,
                        "type": "XSS",
                        "level": 6,
                        "description": "Velit amet quis culpa fugiat sit reprehenderit consectetur. Consequat tempor commodo officia aliqua enim consequat. Adipisicing cillum consectetur dolore velit commodo ad labore elit id tempor. Magna eiusmod sit deserunt ut ad ex ea nisi Lorem. Sunt non adipisicing sint pariatur nostrud officia adipisicing minim nulla cillum laborum aliquip amet est.\r\n"
                    },
                    {
                        "id": 5,
                        "type": "XSS",
                        "level": 5,
                        "description": "Duis nostrud duis in veniam enim. Duis ad consectetur esse proident et cupidatat sunt aliquip nostrud consectetur. Esse sunt consectetur magna velit aute deserunt duis minim.\r\n"
                    },
                    {
                        "id": 6,
                        "type": "SQLi",
                        "level": 4,
                        "description": "Veniam incididunt incididunt eiusmod eiusmod esse do. Minim labore est excepteur incididunt proident Lorem ipsum consectetur dolore irure commodo laboris minim. Velit ad pariatur nulla quis adipisicing magna ullamco. In nisi aliquip magna veniam non excepteur pariatur. Occaecat ex quis velit anim occaecat cupidatat consectetur aliquip adipisicing ad ullamco duis. Elit culpa magna cillum pariatur aliqua sit tempor aliquip.\r\n"
                    },
                    {
                        "id": 7,
                        "type": "SQLi",
                        "level": 4,
                        "description": "Tempor do magna et eiusmod cillum ullamco excepteur adipisicing fugiat id eiusmod. Esse dolor consectetur aute velit velit sit commodo proident laborum. Do pariatur occaecat cillum minim ipsum cupidatat culpa. Magna ipsum deserunt eiusmod aliqua incididunt exercitation esse nisi duis est Lorem cupidatat. Ipsum qui fugiat nulla aliquip sunt ea laborum. Laboris esse cupidatat ea occaecat labore enim ut do tempor duis.\r\n"
                    }
                ]
            },
            {
                "type": "url",
                "vulnerabilities": [
                    {
                        "id": 0,
                        "type": "SQLi",
                        "level": 1,
                        "description": "Id amet aliquip pariatur nisi excepteur officia ex occaecat dolor. Cillum ex mollit consectetur incididunt laborum laborum eiusmod. Mollit qui consequat deserunt incididunt labore ad consequat minim Lorem sit elit nostrud. Velit eiusmod amet do irure labore ullamco sint commodo incididunt. Nostrud do occaecat et aliqua cupidatat ipsum officia sunt id culpa. Consequat aute et id ipsum esse nulla qui eu.\r\n"
                    },
                    {
                        "id": 1,
                        "type": "Other",
                        "level": 6,
                        "description": "Id nisi irure sit aute dolor eu elit tempor eiusmod sint aute consectetur elit labore. Do ea cupidatat exercitation Lorem aliquip esse labore veniam nisi nostrud. In sit proident proident minim sit nisi id. Qui eiusmod eiusmod quis adipisicing et sunt magna qui voluptate. Amet occaecat eu velit dolore nulla eiusmod esse cupidatat amet sunt. Nulla nulla adipisicing pariatur adipisicing ullamco minim eiusmod non mollit aute culpa amet in occaecat. Amet consequat ut tempor commodo elit commodo est incididunt occaecat et deserunt Lorem.\r\n"
                    },
                    {
                        "id": 2,
                        "type": "SQLi",
                        "level": 1,
                        "description": "Non cillum exercitation tempor laborum. Eu non cillum incididunt voluptate ea officia irure labore occaecat in sint voluptate aliqua. Elit culpa anim magna incididunt aliqua in laborum est eu duis esse. Consectetur Lorem minim proident sit proident laborum ut enim quis sint. Eu dolor dolor labore et consequat in sint labore. Magna nulla proident cillum qui. Do cillum elit adipisicing consectetur et occaecat consequat aliquip mollit consequat esse exercitation.\r\n"
                    },
                    {
                        "id": 3,
                        "type": "XSS",
                        "level": 5,
                        "description": "Aute tempor fugiat aliqua ex do. Sit minim fugiat nostrud eu eu occaecat veniam. Do velit culpa qui consectetur nisi.\r\n"
                    },
                    {
                        "id": 4,
                        "type": "SQLi",
                        "level": 3,
                        "description": "Elit nostrud irure duis voluptate aute ea esse ex sunt ea. Reprehenderit deserunt veniam consectetur dolore. Mollit occaecat aliqua elit aliqua velit in est ut sunt est qui sunt. Nisi dolor exercitation consectetur tempor id aute tempor id consequat incididunt sit reprehenderit. Incididunt est proident tempor fugiat commodo dolor non adipisicing nostrud et. Ex anim anim non sunt. Voluptate excepteur ipsum Lorem laborum laborum eiusmod id adipisicing sint cillum sit.\r\n"
                    },
                    {
                        "id": 5,
                        "type": "SQLi",
                        "level": 5,
                        "description": "Duis duis qui nisi voluptate eu fugiat esse ex esse officia minim tempor cillum. Voluptate nisi enim sint esse cillum occaecat elit commodo. Adipisicing tempor mollit Lorem laborum quis nisi eu excepteur consectetur. Adipisicing minim tempor cupidatat ad cupidatat cillum velit dolore excepteur sint pariatur ad esse. Ipsum esse do et cupidatat laboris non.\r\n"
                    },
                    {
                        "id": 6,
                        "type": "Other",
                        "level": 6,
                        "description": "Sunt mollit occaecat id officia. Do aute cupidatat est tempor nostrud Lorem cillum anim elit mollit aliqua sit est. Dolore elit voluptate laborum veniam ex velit ullamco mollit pariatur laborum consectetur. Et cupidatat voluptate fugiat voluptate eiusmod tempor cillum Lorem proident amet quis. Enim ad exercitation non sunt veniam quis tempor.\r\n"
                    },
                    {
                        "id": 7,
                        "type": "XSS",
                        "level": 4,
                        "description": "Consectetur ad eu sunt dolore ad nulla non. Sint excepteur voluptate non velit sint quis ex sint. Nisi anim amet in sit cillum proident velit enim non officia occaecat magna. Non veniam sit veniam labore anim minim adipisicing culpa aliquip laborum in cupidatat sint voluptate. Voluptate do amet eiusmod minim. Anim incididunt consequat qui irure ex excepteur commodo occaecat quis occaecat mollit quis duis nulla.\r\n"
                    }
                ]
            },
            {
                "type": "ip",
                "vulnerabilities": [
                    {
                        "id": 0,
                        "type": "Other",
                        "level": 6,
                        "description": "Aliqua enim aute anim id fugiat amet aliquip in magna eu adipisicing sunt culpa nulla. Sit exercitation incididunt est veniam. Aliquip fugiat occaecat anim est consectetur id sit mollit dolore. Dolor anim eu do velit exercitation qui fugiat. Minim aliqua exercitation irure adipisicing.\r\n"
                    },
                    {
                        "id": 1,
                        "type": "XSS",
                        "level": 1,
                        "description": "Ea laboris magna esse mollit aliqua occaecat esse anim. Voluptate aliqua cillum proident consequat. Voluptate consequat pariatur ut voluptate. Adipisicing consequat tempor irure eiusmod do laborum ad enim reprehenderit tempor.\r\n"
                    },
                    {
                        "id": 2,
                        "type": "Other",
                        "level": 1,
                        "description": "Quis pariatur laborum mollit dolore. Ex dolore nulla eu adipisicing laborum qui et voluptate veniam quis eu. Magna irure eu velit proident cupidatat excepteur. Magna nulla excepteur magna esse esse velit.\r\n"
                    },
                    {
                        "id": 3,
                        "type": "SQLi",
                        "level": 2,
                        "description": "Quis mollit sit velit cupidatat labore ipsum adipisicing veniam voluptate commodo ut. Tempor pariatur elit et cillum mollit qui sunt incididunt nisi culpa. Amet irure deserunt et ullamco incididunt ex eu mollit occaecat.\r\n"
                    },
                    {
                        "id": 4,
                        "type": "SQLi",
                        "level": 5,
                        "description": "Elit culpa commodo sit ad et deserunt anim consectetur dolore est ex. Adipisicing minim exercitation culpa ipsum ullamco enim eiusmod proident minim aliquip excepteur adipisicing sint. Sint non est nisi nulla aute. Excepteur nisi elit mollit enim minim. Ea fugiat veniam nostrud culpa nulla reprehenderit aute adipisicing ea voluptate.\r\n"
                    },
                    {
                        "id": 5,
                        "type": "Other",
                        "level": 2,
                        "description": "Minim pariatur nulla et pariatur laborum excepteur elit ullamco. Sint velit minim aliquip minim consequat. Est dolore ad minim mollit magna eiusmod cillum. Est officia eu sint Lorem. Enim excepteur cillum excepteur nisi deserunt.\r\n"
                    },
                    {
                        "id": 6,
                        "type": "SQLi",
                        "level": 5,
                        "description": "Amet occaecat duis nulla labore. Consequat cillum consectetur qui pariatur duis ea dolore quis. Consequat culpa proident culpa dolore reprehenderit enim anim ad et deserunt qui. Veniam in labore labore laboris quis ad ipsum amet consectetur. Dolor cillum elit non elit consequat quis aliquip et consequat. Exercitation reprehenderit ad in aliquip.\r\n"
                    }
                ]
            }
        ]
    }
]