from app.user.models.models import Technologies,Queries,Opinion,Comments,User
import ast

def replace_with_ids(list_of_tech):
    ids_list=[]
    for itr_tech in list_of_tech:
        tech_id=Technologies.query.filter_by(name = itr_tech).first()
        if tech_id:
            ids_list.append(tech_id.id)
    ids_list=f"{ids_list}"
    return ids_list

def string_list_string(technology):
    tech_list = []

    technology = ast.literal_eval(technology)
    print("technology=", technology, type(technology))

    temp_str = technology[0]
    print("temp_str=", temp_str, type(temp_str))
    my_list = list(temp_str.split(", "))
    print("my_list=", my_list, type(my_list))

    for itr in my_list:
        print(itr, type(itr))
        tech = Technologies.query.filter_by(name=itr).first()
        tech_id = tech.id
        print(tech_id)
        tech_list.append(tech_id)
        print(tech_list)

    print("tech_list=", type(tech_list[0]))
    my_string = ','.join([str(x) for x in tech_list])
    print("my_string= ", my_string)
    return my_string

def user_serializer(user):
    technology = ast.literal_eval(str(user.technology))
    tech_list = []

    for itr in technology:
        tech_check = Technologies.query.filter_by(id=int(itr)).first()
        if tech_check:
            tech_list.append(tech_check.name)

    dt = {
        'name': user.name,
        'user_id': user.id,
        'email': user.email,
        'mobile': user.mobile,
        'technology': tech_list,
        'role':user.roles,
        'updated_at':user.updated_at,
    }
    return dt

def query_serializer(query_obj):
    dt = {
        'query_id':query_obj.id,
        'user_id':query_obj.u_id,
        'title':query_obj.title,
        'description':query_obj.description,
        'filename':query_obj.filename,
        'filepath':query_obj.file_path,
        'technology_id':query_obj.t_id,
        'updated_at':query_obj.updated_at
        #'status':query_obj.status
    }
    return dt


def comments_serializer(comments_obj):
    query_name = Queries.query.filter_by(id=comments_obj.q_id).first()
    liked_disliked_or_not = Opinion.query.filter(and_(LikesDislikes.u_id == user_id,
                                                            LikesDislikes.c_id == comments_obj.id)).first()
    print(liked_disliked_or_not)

    dt = {
        'comment_id': comments_obj.id,
        'user_id': comments_obj.u_id,
        'name': (User.query.filter_by(id=comments_obj.u_id).first()).name,
        'query_id': comments_obj.q_id,
        'msg': comments_obj.msg,
        'like_count': comments_obj.like_count,
        'dislike_count': comments_obj.dislike_count,
        'updated_at': comments_obj.updated_at,
        'title': query_name.title,
        'description': query_name.description
        # 'status':comments_obj.status
    }
    try:
        dt['user_like_status'] = liked_disliked_or_not.like_status
        dt['user_dislike_status'] = liked_disliked_or_not.dislike_status
    except:
        dt['user_like_status'] = False
        dt['user_dislike_status'] = False
    return dt

    # dt = {
    #     'user_id':comments_obj.u_id,
    #     'query_id': comments_obj.q_id,
    #     'msg':comments_obj.msg,
    #     'like_count':comments_obj.like_count,
    #     'dislike_count':comments_obj.dislike_count,
    #     'updated_at':comments_obj.updated_at
    #     #'status':comments_obj.status
    # }
    # return dt
# def query_serializer(convert_to_dict):
#     return {"user_id":convert_to_dict.id,"query_id":convert_to_dict.id,"query_title":convert_to_dict.title,"description":convert_to_dict.description,"technology":convert_to_dict.t_ids}

def technology_serializer(tech_obj):
    dt={
        'tech_id':tech_obj.id,
        'name':tech_obj.name,
        'updated_at':tech_obj.updated_at
    }
    return dt

def opinion_serializer(opinion_obj):

    dt = {
        'user_id': opinion_obj.u_id,
        'like_status': opinion_obj.like_status,
        'dislike_status': opinion_obj.dislike_status,
        'comment_id': opinion_obj.c_id
    }
    try:
        like_dislike_count_find = Comments.query.filter_by(id=like_dislike_obj.c_id).first()
        dt["comment_like_count"] = like_dislike_count_find.like_count
        dt["comment_dislike_count"] = like_dislike_count_find.dislike_count
    except:
        dt["comment_like_count"] = False
        dt["comment_dislike_count"] = False
    return dt

    # dt={
    #     'u_id':opinion_obj.u_id,
    #     'q_id':opinion_obj.q_id,
    #     'c_id':opinion_obj.c_id
    # }
    # return dt

def admin_serializer(admin):
    dt={
        'name': admin.name,
        'user_id': admin.id,
        'role_id': admin.roles,
        'email_id':admin.email,
        'mobile': admin.mobile
    }
    return dt

def ticket_serializer(ticket):
    dt={
        'user_id':ticket.u_id,
        'title':ticket.title,
        'problem':ticket.problem
    }
    return dt

def saved_query_serializer(saved_query):


    # saved_query_obj=Queries.query.filter_by(u_id=saved_query.u_id).all()
    # print(saved_query_obj)

    dt = {
        'user_id': saved_query.u_id,
        'query_id':saved_query.id,
        'title': saved_query.title,
        'description': saved_query.description,
        'filename':saved_query.filename,
        'filepath':saved_query.filepath
    }
    return dt