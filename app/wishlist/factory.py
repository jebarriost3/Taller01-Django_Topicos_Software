
class WishlistManager:
    def __init__(self, request):
        self.request = request

    def get(self):
        return self.request.session.get('wishlist', [])

    def save(self, wishlist):
        self.request.session['wishlist'] = wishlist
        self.request.session.modified = True

    def add(self, producto_id):
        wishlist = self.get()
        if producto_id not in wishlist:
            wishlist.append(producto_id)
        self.save(wishlist)

    def remove(self, producto_id):
        wishlist = self.get()
        if producto_id in wishlist:
            wishlist.remove(producto_id)
        self.save(wishlist)

def get_wishlist_manager(request):
    return WishlistManager(request)
