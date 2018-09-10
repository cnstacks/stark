# by luffycity.com
from django.conf.urls import url

from django.shortcuts import HttpResponse,render,redirect
from django.urls import reverse

from django.utils.safestring import mark_safe

class ModelStark(object):

    list_display=["__str__",]
    list_display_links=[]
    modelform_class=None


    def __init__(self,model,site):
        self.model=model
        self.site=site


    # 删除 编辑，复选框
    def edit(self,obj=None,header=False):
        if header:
            return "操作"
        #return mark_safe("<a href='%s/change'>编辑</a>"%obj.pk)
        _url=self.get_change_url(obj)


        print("_url",_url)



        return mark_safe("<a href='%s'>编辑</a>"%_url)

    def deletes(self,obj=None,header=False):
        if header:
            return "操作"
        # return mark_safe("<a href='%s/change'>编辑</a>"%obj.pk)

        _url=self.get_delete_url(obj)

        return mark_safe("<a href='%s'>删除</a>" % _url)

    def checkbox(self,obj=None,header=False):
        if header:
            return mark_safe('<input id="choice" type="checkbox">')

        return mark_safe('<input class="choice_item" type="checkbox">')

    def get_modelform_class(self):

        if not self.modelform_class:
            from django.forms import ModelForm
            from django.forms import widgets as wid
            class ModelFormDemo(ModelForm):
                class Meta:
                    model = self.model
                    fields = "__all__"
                    labels={
                        ""
                    }
            return ModelFormDemo
        else:
            return self.modelform_class

    def add_view(self, request):
        ModelFormDemo = self.get_modelform_class()
        if request.method=="POST":
            form = ModelFormDemo(request.POST)
            if form.is_valid():
                form.save()
                return redirect(self.get_list_url())

            return render(request, "add_view.html", locals())

        form=ModelFormDemo()

        return render(request,"add_view.html",locals())

    def delete_view(self, request, id):
        url = self.get_list_url()
        if request.method=="POST":
            self.model.objects.filter(pk=id).delete()
            return redirect(url)

        return render(request,"delete_view.html",locals())

    def change_view(self, request, id):
        ModelFormDemo = self.get_modelform_class()
        edit_obj = self.model.objects.filter(pk=id).first()

        if request.method=="POST":
            form = ModelFormDemo(request.POST,instance=edit_obj)
            if form.is_valid():
                form.save()
                return redirect(self.get_list_url())

            return render(request, "add_view.html", locals())



        form = ModelFormDemo(instance=edit_obj)

        return render(request, "change_view.html", locals())

    def new_list_play(self):
        temp=[]
        temp.append(ModelStark.checkbox)
        temp.extend(self.list_display)
        if not self.list_display_links:
            temp.append(ModelStark.edit)
        temp.append(ModelStark.deletes)
        return temp


    def get_change_url(self,obj):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label

        _url = reverse("%s_%s_change" % (app_label, model_name), args=(obj.pk,))

        return _url

    def get_delete_url(self, obj):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label

        _url = reverse("%s_%s_delete" % (app_label, model_name), args=(obj.pk,))

        return _url


    def get_add_url(self):

        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label

        _url = reverse("%s_%s_add" % (app_label, model_name))

        return _url

    def get_list_url(self):

        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label

        _url = reverse("%s_%s_list" % (app_label, model_name))

        return _url

    def list_view(self, request):
        print(self.model) # UserConfig(Userinfo).model
        print("list_dispaly",self.list_display)

        data_list=self.model.objects.all() # 【obj1,obj2,....】

        # 构建表头
        header_list=[]
        print("header",self.new_list_play())  #  [checkbox,"pk","name","age",edit ,deletes]     【checkbox ,"__str__", edit ,deletes】

        for field in self.new_list_play():

            if callable(field):
                #header_list.append(field.__name__)
                val=field(self,header=True)
                header_list.append(val)

            else:
                if field=="__str__":
                     header_list.append(self.model._meta.model_name.upper())
                else:
                    #header_list.append(field)
                    val=self.model._meta.get_field(field).verbose_name
                    header_list.append(val)



        # 构建表单数据
        new_data_list=[]
        for obj in data_list:
            temp=[]

            for filed in  self.new_list_play(): # ["__str__",]      ["pk","name","age",edit]

                if callable(filed):
                    val=filed(self,obj)
                else:
                    val=getattr(obj,filed)
                    if filed in self.list_display_links:

                        # "app01/userinfo/(\d+)/change"
                        _url=self.get_change_url(obj)

                        val=mark_safe("<a href='%s'>%s</a>"%(_url,val))

                temp.append(val)

            new_data_list.append(temp)

        '''
        [
            [1,"alex",12],
            [1,"alex",12],
            [1,"alex",12],
            [1,"alex",12],
           
                 ]

        '''

        print(new_data_list)
        # 构建一个查看URL
        add_url=self.get_add_url()
        return render(request, "list_view.html", locals())

    def get_urls_2(self):

        temp = []

        model_name=self.model._meta.model_name
        app_label=self.model._meta.app_label

        temp.append(url(r"^add/", self.add_view,name="%s_%s_add"%(app_label,model_name)))
        temp.append(url(r"^(\d+)/delete/", self.delete_view,name="%s_%s_delete"%(app_label,model_name)))
        temp.append(url(r"^(\d+)/change/", self.change_view,name="%s_%s_change"%(app_label,model_name)))
        temp.append(url(r"^$", self.list_view,name="%s_%s_list"%(app_label,model_name)))

        return temp

    @property
    def urls_2(self):
        print(self.model)
        return self.get_urls_2(), None, None


class StarkSite(object):
    def __init__(self):
        self._registry={}

    def register(self,model,stark_class=None):
        if not stark_class:
            stark_class=ModelStark

        self._registry[model] = stark_class(model, self)


    def get_urls(self):
        temp=[]
        for model,stark_class_obj in self._registry.items():
            model_name=model._meta.model_name
            app_label=model._meta.app_label
            # 分发增删改查
            temp.append(url(r"^%s/%s/"%(app_label,model_name),stark_class_obj.urls_2))

            '''
            url(r"^app01/userinfo/",UserConfig(Userinfo).urls_2),
            url(r"^app01/book/",ModelStark(Book).urls_2), 
            
        
            '''
        return temp

    @property
    def urls(self):

       return self.get_urls(),None,None

site=StarkSite()












