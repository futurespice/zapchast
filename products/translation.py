from modeltranslation.translator import register, TranslationOptions
from .models import Product, Category, Subcategory

@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Subcategory)
class SubcategoryTranslationOptions(TranslationOptions):
    fields = ('name',)