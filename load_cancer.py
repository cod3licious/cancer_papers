import os
from glob import glob


def articles2dict(label='keyword', reduced_labels=False, combine_paragraphs=True, ignore_types=['Mixed'], verbose=1):
    """
    Load the cancer papers dataset

    Input:
        - label: possible values 'keyword' and 'partype', what should be used as labels in doccats,
                 i.e. whether you want to classify the papers as being written about different cancer types
                 or as paragraphs belonging to different types such as abstract or results
        - reduced_labels: if the "bla bla" paragraphs (Abstract, Introduction, Discussion)
                 should be summarized as a single class (default: False)
        - combine_paragraphs: only in case of label='keyword': if all paragraphs of a paper should be collapsed into
                 a single text (default: True)
        - ignore_types: a list of paragraph types which should be ignored (by default, unidentified 'Mixed' paragraphs)
        - verbose: verbosity level (default: 1)

    Returns:
        - textdict: a dictionary with {'document id': 'text'}
        - doccats: a corresponding dictionary with {'document id': 'label'}
        - catdesc: a dictionary with {'label': 'label description'}
    """
    textdict = {}
    doccats = {}
    catdesc = {}
    current_path = __file__[:-(len(__file__.split('/')[-1]) + 1)]
    for keyword in ['brain_cancer', 'breast_cancer', 'colorectal_cancer', 'kidney_cancer', 'leukemia_cancer',
                    'lung_cancer', 'lymphoma_cancer', 'melanoma_cancer', 'pancreatic_cancer', 'prostate_cancer']:
        if verbose:
            print("processing: %s" % keyword)
        for tfile in glob('%s/pmc_preproc/%s/*.txt' % (current_path, keyword)):
            pmcid = os.path.splitext(os.path.basename(tfile))[0]
            # read in all paragraphs and store them with their respective type
            paragraphs = {}
            with open(tfile) as f:
                lines = f.readlines()
                partypes = lines[0].strip()[1:-1]
                partypes = partypes.split(', ')
                for par in lines[1:]:
                    par = par.strip()
                    # if it's an empty line, move on to the next partype
                    if not par:
                        if not partypes:
                            print("WARNING: more paragraph types found then specified!")
                            print(tfile)
                        ptype = partypes.pop(0)
                        # deal with special cases
                        if reduced_labels and ptype in ('Abstract', 'Introduction', 'Discussion'):
                            ptype = 'Abs/Intro/Disc'
                        continue
                    if ptype in ignore_types:
                        continue
                    # make sure it's more than just a short title
                    elif len(par.split()) > 4:
                        try:
                            paragraphs[ptype] += "\n" + par
                        except KeyError:
                            paragraphs[ptype] = par
                if partypes:
                    print("WARNING: too many paragraph types specified!")
                    print(tfile)
            if label == 'keyword':
                if combine_paragraphs:
                    # {pmcid: text} and {pmcid: keyword}
                    text = "\n".join([paragraphs[ptype] for ptype in ['Abstract', 'Introduction', 'Discussion',
                                                                      'Abs/Intro/Disc', 'Mixed', 'Methods', 'Results'] if ptype in paragraphs])
                    if text:
                        textdict[pmcid] = text
                        doccats[pmcid] = keyword
                else:
                    # {'pmcid partype': text} and {'pmcid partype': keyword}
                    for ptype in paragraphs:
                        textdict['%s %s' % (pmcid, ptype)] = paragraphs[ptype]
                        doccats['%s %s' % (pmcid, ptype)] = keyword
            else:
                # {'pmcid partype': text} and {'pmcid partype': partype}
                for ptype in paragraphs:
                    textdict['%s %s' % (pmcid, ptype)] = paragraphs[ptype]
                    doccats['%s %s' % (pmcid, ptype)] = ptype
    catdesc = {d: d for d in set(doccats.values())}
    return textdict, doccats, catdesc


if __name__ == '__main__':
    # load all articles with full text; as a label use the cancer type
    textdict, doccats, catdesc = articles2dict(label='keyword', ignore_types=[])
    # load only the abstracts of all articles; as a label use the cancer type
    textdict, doccats, catdesc = articles2dict(label='keyword', ignore_types=[
                                               'Introduction', 'Discussion', 'Mixed', 'Methods', 'Results'])
    # load all paragraphs from all papers except those labeled 'Mixed'; as
    # label have the paragraph type but group Abstract/Intro/Discussion
    textdict, doccats, catdesc = articles2dict(label='partype', reduced_labels=True, ignore_types=['Mixed'])
