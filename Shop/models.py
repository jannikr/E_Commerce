from django.db import models
from Profile.models import ShopUser


# Create your models here.
class Product(models.Model):
    PRODUCT_CATEGORIES = [
        ('L', 'Landschaft'),
        ('P', 'Portrait'),
        ('U', 'Urban'),
        ('S', 'Sport'),
        ('A', 'Artwork'),
        ('M', 'Makro'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.FloatField()
    creator = models.ForeignKey(ShopUser,
                                on_delete=models.CASCADE,
                                related_name='user',
                                related_query_name='users')
    image = models.ImageField(null=True)
    category = models.CharField(max_length=1,
                                choices=PRODUCT_CATEGORIES,
                                )

    class Meta:
        ordering = ['creator', 'title']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    # TODO fix onestar bug
    # one stars

    def get_onestars(self):
        onestars = Vote.objects.filter(rating='O', product=self)
        return onestars

    def get_onestar_count(self):
        return len(self.get_onestars())

    # two stars

    def get_twostars(self):
        twostars = Vote.objects.filter(rating='TW', product=self)
        return twostars

    def get_twostar_count(self):
        return len(self.get_twostars())

    # three stars

    def get_threestars(self):
        threestars = Vote.objects.filter(rating='TH', product=self)
        return threestars

    def get_threestar_count(self):
        return len(self.get_threestars())

    # four stars

    def get_fourstars(self):
        fourstars = Vote.objects.filter(rating='FO', product=self)
        return fourstars

    def get_fourstar_count(self):
        return len(self.get_fourstars())

    # five stars

    def get_fivestars(self):
        fivestars = Vote.objects.filter(rating='FI', product=self)
        return fivestars

    def get_fivestar_count(self):
        return len(self.get_fivestars())

    # get average

    def get_average(self):
        zaehler = self.get_onestar_count() * 1 + self.get_twostar_count() * 2 + self.get_threestar_count() * 3 + self.get_fourstar_count() * 4 + self.get_fivestar_count() * 5
        nenner = ((
                self.get_onestar_count() + self.get_twostar_count() + self.get_threestar_count() + self.get_fourstar_count() + self.get_fivestar_count()))
        if (nenner != 0):
            avg = zaehler / nenner
        else:
            avg = 0
        return avg

    def get_number_of_votes(self):
        return (len(Vote.objects.filter(product=self)))

    def vote(self, user, rating):
        # when the user has not voted before
        if not (len(Vote.objects.filter(shopUser=user, product=self)) > 0):
            vote = Vote.objects.create(rating=rating,
                                       shopUser=user,
                                       product=self
                                       )
        # when the user voted before but with a different rating value
        selectedUser = Vote.objects.filter(shopUser=user, product=self)
        if not (str(rating) in str(selectedUser[0])):
            # delete old value -> no duplicates
            Vote.objects.get(shopUser=user, product=self).delete()
            # create the new value
            Vote.objects.create(rating=rating, shopUser=user, product=self)


class Order(models.Model):
    shopUser = models.ForeignKey(ShopUser, on_delete=models.SET_NULL, blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=20, null=True)

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    def newItem(self, product, quantity):
        quantity = 1
        OrderItem.objects.create(product=product, quantity=quantity, order=self)

    def __str__(self):
        return str(self.shopUser.username) + ' (' + str(self.date_ordered) + ')'


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

    def __str__(self):
        return self.product.title + ' (' + str(self.quantity) + ')'





class Vote(models.Model):
    VOTE_TYPES = [
        ('O', 'one'),
        ('TW', 'two'),
        ('TH', 'three'),
        ('FO', 'four'),
        ('FI', 'five'),
    ]

    rating = models.CharField(max_length=2,
                              choices=VOTE_TYPES,
                              )
    timestamp = models.DateTimeField(auto_now_add=True)
    shopUser = models.ForeignKey(ShopUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.rating + ' on ' + self.product.title + ' by ' + self.shopUser.username


class Comment(models.Model):
    text = models.TextField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(ShopUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def get_comment_prefix(self):
        if len(self.text) > 50:
            return self.text[:50] + '...'
        else:
            return self.text

    def get_downvotes(self):
        downvotes = Vote_Comment.objects.filter(up_or_down_or_flag='D', comment=self)
        return downvotes

    def get_downvotes_count(self):
        return len(self.get_downvotes())

    def get_upvotes(self):
        upvotes = Vote_Comment.objects.filter(up_or_down_or_flag='U', comment=self)
        return upvotes

    def get_upvotes_count(self):
        return len(self.get_upvotes())

    def get_flags(self):
        flags = Vote_Comment.objects.filter(up_or_down_or_flag='F', comment=self)
        return flags

    def get_flags_count(self):
        return len(self.get_flags())

    def vote(self, user, up_or_down_or_flag):
        # TODO only one vote
        print(self)
        Vote_Comment.objects.create(up_or_down_or_flag=up_or_down_or_flag,
                                    shopUser=user,
                                    comment=self
                                    )

    def __str__(self):
        return self.get_comment_prefix() + ' (' + self.user.username + ')'

    def __repr__(self):
        return self.get_comment_prefix() + ' (' + self.user.username + ' / ' + str(self.timestamp) + ')'


class Vote_Comment(models.Model):
    VOTE_TYPES = [
        ('U', 'up'),
        ('D', 'down'),
        ('F', 'flag'),
    ]

    up_or_down_or_flag = models.CharField(max_length=1,
                                          choices=VOTE_TYPES, null=True,
                                          )
    timestamp = models.DateTimeField(auto_now_add=True)
    shopUser = models.ForeignKey(ShopUser, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(
            self.up_or_down_or_flag) + ' on ' + self.comment.get_comment_prefix() + ' by ' + self.shopUser.username
