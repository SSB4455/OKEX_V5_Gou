using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class NewBehaviourScript : MonoBehaviour
{
    public Text outPutText;
    public float initCash = 1000;
    public float loss = -0.1f;
    public float gran = 0.05f;
    float lastValue = -1;
    Vector2 positionToCash = Vector2.zero;

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void ValueChange(float value)
    {
        float all = initCash;
        if (positionToCash[0] == 0)
        {
            positionToCash[0] = all / 2 / value;
            positionToCash[1] = all / 2;
        }
        else if (value * positionToCash[0] < positionToCash[1] * 0.9f)
        {
            all = value * positionToCash[0] + positionToCash[1];
            positionToCash[0] = all / 2 / value;
            positionToCash[1] = all / 2;
        }
        else if (value * positionToCash[0] > positionToCash[1] * 1.05f)
        {
            all = value * positionToCash[0] + positionToCash[1];
            positionToCash[0] = all / 2 / value;
            positionToCash[1] = all / 2;
        }
        string line = "value = " + value + " -> (" + positionToCash[0] + "," + positionToCash[1] + ")" + (positionToCash[0] * value + positionToCash[1]);
        outPutText.text = line + "\n" + outPutText.text;
        Debug.Log(line);
    }
}
