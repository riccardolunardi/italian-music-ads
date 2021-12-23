class ProxyManager:

    def __init__(self, file_proxy, limite):
        self.limite = limite
        self.uso_proxy = 0
        self.proxy_corrente = 0
        self.proxy_list = []

        with open(file_proxy, 'r') as f:
            for line in f:
                line = line.replace('\n','')
                tmp = line.split(':')

                proxies = {
                    'http': 'http://'+ tmp[2] + ':' + tmp [3] + '@' + tmp [0] + ':' + tmp [1] + '/',
                    'https': 'http://'+ tmp[2] + ':' + tmp [3] + '@' + tmp [0] + ':' + tmp [1] + '/',
                }

                self.proxy_list.append(proxies)


    def pick_proxy(self):
        proxy_to_return = self.proxy_list[self.proxy_corrente]
        self.uso_proxy += 1

        if self.uso_proxy % self.limite == 0:
            self.proxy_corrente = (self.proxy_corrente + 1) % len(self.proxy_list)

        return proxy_to_return

    def pick_proxies(self, n):
        proxy_to_return = self.proxy_list[self.proxy_corrente:((self.proxy_corrente+n) % len(self.proxy_list))]
        self.uso_proxy += n

        if len(proxy_to_return) != n:
            proxy_to_return = self.proxy_list[n:]

        if self.uso_proxy % self.limite == 0:
            self.proxy_corrente = (self.proxy_corrente + n) % len(self.proxy_list)

        return proxy_to_return