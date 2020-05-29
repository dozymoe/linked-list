from django import forms


class CreateForm(forms.Form):

    url = forms.URLField(label="URL")


LINK_FIELDS = (
    ('page.url', "URL"),
    ('page.title', "Title"),
    ('page.description', "Description"),
    ('page.keywords', "Keywords"),
    ('page.published_at', "Publish Date"),
    ('page.body.text', "Content"),
    ('page.body.html', "HTML Content"),
    ('page.image.url', "Image"),
    ('page.image.alt', "Image's Description"),
    ('page.image.height', "Image's Height"),
    ('page.image.width', "Image's Width"),
    ('author.name', "Author's Name"),
    ('author.image.url', "Author's Photo"),
    ('author.image.height', "Author's Photo Height"),
    ('author.image.width', "Author's Photo Width"),
    ('author.social', "Author's Social Media"),
    ('publisher.name', "Publisher's Name"),
    ('publisher.image.url', "Publisher's Logo"),
    ('publisher.image.height', "Publisher's Logo Height"),
    ('publisher.image.width', "Publisher's Logo Width"),
    ('publisher.url', "Publisher's Website"),
    ('publisher.social', "Publisher's Social Media"),
)


class CreateChooseForm(forms.Form):

    name = forms.ChoiceField(label="Field's Name", choices=LINK_FIELDS,
            required=True, widget=forms.HiddenInput())
    value = forms.CharField(label="Field's Value", required=True)
