---
title: 【Unity】Unity单例模式
date: 2024-07-05 15:32:06
tags:
  - Unity
  - 设计模式
---



在unity中，经常需要使用到单例，尤其是MonoBehaviour的单例。

MonoBehaviour的单例模式需要使用饿汉模式的单例来初始化，要不然可能会自动创建多出的单例。

### MonoBehaviour单例

```C#
using UnityEngine;

/// <summary>
/// 继承自这个类的单例同样也是MonoBehaviour，可以挂载到物体上，并且会将该物体放置DontDestroyOnLoad内
/// 如果项目本身就使用多场景控制物件，可以不用调用DontDestroyOnLoad方法
/// </summary>
/// <typeparam name="T"></typeparam>
public class MonoSingleton<T> : MonoBehaviour where T : Component
{
    private static T _instance = null;

    public static T Instance
    {
        get
        {
            if (_instance == null)
            {
                _instance = FindObjectOfType<T>();
                if (_instance == null)
                {
                    GameObject obj = new GameObject(typeof(T).Name, new[] {typeof(T)});
                    DontDestroyOnLoad(obj);
                    _instance = obj.GetComponent<T>();
                    (_instance as IInitable)?.Init();
                }
                else
                {
                    Debug.LogWarning("Instance is already exist!");
                }
            }

            return _instance;
        }
    }

    /// <summary>
    /// 继承Mono单例的类如果写了Awake方法，需要在Awake方法最开始的地方调用一次base.Awake()，来给_instance赋值
    /// </summary>
    protected void Awake()
    {
        _instance = this as T;
        DontDestroyOnLoad(this.transform.root);
    }
}
```

### 非MonoBehaviour单例

```C#
/// <summary>
/// 继承自这个类的单例不是MonoBehaviour，无法怪载到物体上
/// </summary>
/// <typeparam name="T"></typeparam>
public class Singleton<T> where T : new()
{
    private static T _instance;

    public static T Instance
    {
        get
        {
            if (_instance == null)
            {
                _instance = new T();
                (_instance as IInitable)?.Init();
            }

            return _instance;
        }
    }
}
```

